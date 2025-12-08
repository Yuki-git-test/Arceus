import re

import discord

from Constants.aesthetic import Emojis_Balls, Emojis_Factions
from Constants.faction_data import FACTION_LOGO_EMOJIS, get_faction_by_emoji
from Constants.vn_allstars_constants import VN_ALLSTARS_ROLES
from utils.cache.cache_list import (
    daily_faction_ball_cache,
    faction_members_cache,
    processed_faction_ball_alerts,
    processed_pokemon_spawn_msgs,
)
from utils.db.daily_faction_ball import update_faction_ball
from utils.db.faction_members import update_faction_member_faction
from utils.logs.debug_log import debug_log, enable_debug
from utils.logs.pretty_log import pretty_log
from utils.pokemeow.get_pokemeow_reply import get_pokemeow_reply_member

FISHING_COLOR = 0x87CEFA


"""enable_debug(f"{__name__}.extract_trainer_name_from_description")
enable_debug(f"{__name__}.get_faction_member_via_trainer_name")
enable_debug(f"{__name__}.faction_ball_alert")
enable_debug(f"{__name__}.pokemon_spawn_listener")"""


def extract_trainer_name_from_description(description: str) -> str | None:
    """
    Extracts the trainer name (e.g. 'khy.09') from a PokéMeow embed description.
    Handles both 'found a wild' and 'fished a wild' scenarios.
    Example lines:
    '<:irida:...>  **khy.09** found a wild ...'
    '<:irida:...>  **khy.09** fished a wild ...'
    """

    match = re.search(r"\*\*(.+?)\*\*\s+(?:found|fished) a wild", description)
    if match:
        debug_log(f"Extracted trainer name: {match.group(1).strip()}")
        return match.group(1).strip()
    return None


def get_faction_member_via_trainer_name(bot, guild: discord.Guild, trainer_name: str):

    debug_log(f"Looking up faction member for trainer_name: {trainer_name}")
    # Get user id via username
    from utils.cache.vna_members_cache import (
        fetch_vna_member_id_by_username_or_pokemeow_name,
    )

    user_id = fetch_vna_member_id_by_username_or_pokemeow_name(trainer_name)
    debug_log(f"Fetched user_id from vna cache: {user_id}")
    if not user_id:
        # Try faction members cache
        from utils.cache.faction_members_cache import (
            fetch_faction_member_id_by_username,
        )

        user_id = fetch_faction_member_id_by_username(trainer_name)
        debug_log(f"Fetched user_id from faction cache: {user_id}")
        if not user_id:
            debug_log(f"No user_id found for trainer_name: {trainer_name}")
            return
    member = guild.get_member(user_id)
    debug_log(f"Fetched member from guild: {member}")
    if not member:
        debug_log(f"No member found in guild for user_id: {user_id}")
        return

    return member


# 🛡️────────────────────────────────────────────
#      🛡️ Faction Ball Alert Listener
# 🛡️────────────────────────────────────────────
async def faction_ball_alert(
    member: discord.Member, before: discord.Message, after: discord.Message
):
    """Listener for faction ball alerts in spawn messages."""

    debug_log(
        f" Called for member: {getattr(member, 'id', None)} | before.id: {getattr(before, 'id', None)} | after.id: {getattr(after, 'id', None)}"
    )
    if not after.embeds or not after.embeds[0].description:
        debug_log(" No embed or description, exiting early.")
        return

    description_text = after.embeds[0].description
    debug_log(f" Description text: {description_text}")

    if description_text and "<:team_logo:" not in description_text:
        debug_log(" No team logo emoji in description.")
        return

    team_logo_emoji = re.findall(r"<:team_logo:\d+>", description_text)
    debug_log(f" Found team logo emojis: {team_logo_emoji}")
    if not team_logo_emoji:
        debug_log(" No team logo emoji found.")
        return

    team_logo_emoji = team_logo_emoji[0]
    debug_log(f" Using team logo emoji: {team_logo_emoji}")

    if after.id in processed_faction_ball_alerts:
        debug_log(f" Message {after.id} already processed.")
        return
    processed_faction_ball_alerts.add(after.id)

    embed_faction = get_faction_by_emoji(team_logo_emoji)
    debug_log(f" Faction from emoji: {embed_faction}")
    if not embed_faction:
        debug_log(" Faction not found for emoji.")
        return

    user_faction_ball_alert = faction_members_cache.get(member.id)
    debug_log(f" Faction member cache for {member.id}: {user_faction_ball_alert}")
    if not user_faction_ball_alert:
        debug_log(f" User {member.id} not in faction members cache.")
        return

    user_faction_ball_notify = user_faction_ball_alert.get("notify")
    user_faction = user_faction_ball_alert.get("faction")
    user_name = member.name
    user_mention = member.mention
    debug_log(
        f" Notify: {user_faction_ball_notify}, Faction: {user_faction}, Name: {user_name}"
    )
    if not user_faction_ball_notify or user_faction_ball_notify.lower() == "off":
        debug_log(f" User {member.id} has notifications off.")
        return

    if not user_faction:
        debug_log(f" User {member.id} has no faction set.")
        await after.channel.send(
            f"{user_mention}, I don't know your faction yet, Can you do `;fa`? Thank you!"
        )
        return

    display_embed_faction_emoji = getattr(Emojis_Factions, embed_faction)
    display_embed_faction = (
        f"{display_embed_faction_emoji} {embed_faction.title()}"
        if display_embed_faction_emoji
        else embed_faction.title()
    )
    debug_log(f" Display faction: {display_embed_faction}")

    faction_ball = daily_faction_ball_cache.get(user_faction)
    debug_log(f" Faction ball for {user_faction}: {faction_ball}")
    if not faction_ball:
        debug_log(f" No daily ball for faction {user_faction}.")
        content = f"{user_mention} I don't know your faction's daily ball yet, can you do `;fa`? Thanks!."
        await after.channel.send(content)
        return

    ball_emoji = getattr(Emojis_Balls, faction_ball.lower())
    debug_log(f" Ball emoji for {faction_ball}: {ball_emoji}")
    if not ball_emoji:
        debug_log(f" Ball emoji not found for {faction_ball}.")
        return

    if user_faction_ball_notify == "on":
        debug_log(f" Sending notification with ping to {user_mention}.")
        content = f"{user_mention}, This Pokemon is a daily {display_embed_faction_emoji} hunt! Use {ball_emoji}!"
        await after.channel.send(content)
    elif user_faction_ball_notify == "on_no_pings":
        debug_log(f" Sending notification without ping to {user_name}.")
        content = f"{user_name}, This Pokemon is a daily {display_embed_faction_emoji} hunt! Use {ball_emoji}!"
        await after.channel.send(content)

    else:
        debug_log(f" Reacting with ball emoji: {ball_emoji}")
        await after.add_reaction(ball_emoji)


async def pokemon_spawn_listener(bot, message: discord.Message):
    debug_log(
        f" Called for message.id: {getattr(message, 'id', None)} | bot: {getattr(bot, 'user', None)}"
    )
    embed = message.embeds[0] if message.embeds else None
    debug_log(f" Embed: {embed}")
    if not embed:
        debug_log(" No embed found, exiting.")
        return

    message_content = message.content
    debug_log(f" Message content: {message_content}")
    if not message_content:
        debug_log(" No message content, exiting.")
        return

    if not "found a wild" in message_content.lower():
        debug_log(" 'found a wild' not in message content, exiting.")
        return

    if message.id in processed_pokemon_spawn_msgs:
        debug_log(f" Message ID {message.id} already processed, exiting.")
        return
    processed_pokemon_spawn_msgs.add(message.id)

    guild = message.guild
    debug_log(f" Guild: {guild}")
    member = await get_pokemeow_reply_member(message)
    debug_log(f" Member from get_pokemeow_reply: {member}")
    if not member:
        trainer_name = extract_trainer_name_from_description(embed.description)
        debug_log(f" Trainer name extracted: {trainer_name}")
        if not trainer_name:
            debug_log(" No trainer name extracted, exiting.")
            return
        member = get_faction_member_via_trainer_name(bot, guild, trainer_name)
        debug_log(f" Member from get_faction_member_via_trainer_name: {member}")
        if not member:
            debug_log(" No member found via trainer name, exiting.")
            return

    if "<:team_logo:" in embed.description:
        faction_member = faction_members_cache.get(member.id)
        debug_log(
            f" Faction member cache for {getattr(member, 'id', None)}: {faction_member}"
        )
        if not faction_member:
            debug_log(
                f" No faction member found in cache for {getattr(member, 'id', None)}, exiting."
            )
            return

        user_faction_notify = faction_member.get("notify")
        debug_log(f" user_faction_notify: {user_faction_notify}")

        if user_faction_notify and user_faction_notify.lower() != "off":
            debug_log(
                f" Notifying via faction_ball_alert for member {getattr(member, 'id', None)}."
            )
            await faction_ball_alert(member, message, message)

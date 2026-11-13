import re

import discord

from Constants.faction_data import FACTION_LOGO_EMOJIS, get_faction_by_emoji
from Constants.vn_allstars_constants import VN_ALLSTARS_ROLES, VNA_SERVER_ID
from utils.cache.cache_list import daily_faction_ball_cache, faction_members_cache
from utils.db.daily_faction_ball import update_faction_ball
from utils.db.faction_members import (
    update_faction_member_faction,
    upsert_faction_member,
)
from utils.logs.debug_log import debug_log, enable_debug
from utils.logs.pretty_log import pretty_log
from utils.pokemeow.get_pokemeow_reply import get_pokemeow_reply_member


# 🛡️────────────────────────────────────────────
#      🛡️ Faction Ball Listener Functions
# 🛡️────────────────────────────────────────────
async def extract_faction_ball_from_daily(bot, message: discord.Message):
    """Listens to PokéMeow's daily message for faction ball info."""
    debug_log("Starting extract_faction_ball_from_daily")
    embed = message.embeds[0] if message.embeds else None
    if not embed:
        debug_log("No embed found in daily message.")
        return

    embed_description = embed.description or ""
    debug_log(f"Embed description: {embed_description}")
    if not embed_description:
        debug_log("No description found in embed.")
        return

    # Regex to match: <:team_logo:ID> **|** Your Faction's daily ball-type is <:ball_emoji:ID> BallName
    match = re.search(
        r"(<:team_logo:\d+>) \*\*\|\*\* Your Faction's daily ball-type is (<:[^:]+:\d+>) ([A-Za-z]+)",
        embed.description,
    )
    debug_log(f"Regex match result: {match}")
    if not match:
        pretty_log(
            "info",
            "Could not find faction ball info in daily message.",
            bot=bot,
        )
        return

    faction_team_emoji = match.group(1)
    daily_ball_emoji = match.group(2)
    daily_ball_name_match = re.search(r"<:([a-zA-Z0-9_]+):\d+>", daily_ball_emoji)
    daily_ball = (
        daily_ball_name_match.group(1).lower() if daily_ball_name_match else None
    )
    debug_log(
        f"Matched faction_team_emoji: {faction_team_emoji}, daily_ball_emoji: {daily_ball_emoji}, daily_ball: {daily_ball}"
    )
    if not daily_ball:
        debug_log("Could not extract ball name from emoji.")
        return
    pretty_log(
        "info",
        f"Extracted faction ball from daily message in {message.channel.name}: Faction Emoji: {faction_team_emoji}, Ball: {daily_ball}",
        bot=bot,
    )
    faction = get_faction_by_emoji(faction_team_emoji)
    debug_log(f"Faction resolved from emoji: {faction}")
    if not faction:
        pretty_log(
            "info",
            f"Could not determine faction from emoji {faction_team_emoji} in daily message.",
            bot=bot,
        )
        return

    member = await get_pokemeow_reply_member(message)
    debug_log(f"Member resolved from message: {member}")
    if not member:
        debug_log("No member found from get_pokemeow_reply_member.")
        return

    # Check if there is already a ball for that faction
    latest_ball = daily_faction_ball_cache.get(faction)
    debug_log(f"Latest ball in cache for faction {faction}: {latest_ball}")

    if latest_ball != daily_ball:
        debug_log(f"Updating faction ball for {faction}: {latest_ball} -> {daily_ball}")
        # Update db and cache
        await update_faction_ball(bot, faction, daily_ball)
    else:
        debug_log(f"No update needed for faction {faction}, ball unchanged.")

    # Check if user has faction or not
    user_id = member.id
    user_name = member.name
    cached_member = faction_members_cache.get(user_id)
    debug_log(f"Cached member for user_id {user_id}: {cached_member}")
    if not cached_member:
        # Upsert user with faction
        debug_log(
            f"No cached member found for user {user_id}. Upserting with faction {faction}."
        )
        clan_name = "Other"
        if message.guild and message.guild.id == VNA_SERVER_ID:
            vna_role = message.guild.get_role(VN_ALLSTARS_ROLES.vna_member)
            if vna_role and vna_role in member.roles:
                clan_name = "VNA"
        await upsert_faction_member(
            bot=bot,
            user_id=user_id,
            user_name=user_name,
            faction=faction,
            clan_name=clan_name,
            notify="on_no_pings",
        )
        return

    existing_user_faction = cached_member.get("faction")
    debug_log(f"User's current faction: {existing_user_faction}")
    if not existing_user_faction or existing_user_faction != faction:
        debug_log(f"Updating user {user_id} faction to {faction}")
        # Update user faction
        await update_faction_member_faction(bot, user_id, faction)
        pretty_log(
            "success",
            f"Updated faction for user {user_id} to '{faction}' based on daily message.",
            bot=bot,
        )
    else:
        debug_log(f"User {user_id} already has faction: {existing_user_faction}")


# 🛡️────────────────────────────────────────────
#      🛡️ Extract Faction Ball from Faction Command
# 🛡️────────────────────────────────────────────
async def extract_faction_ball_from_fa(bot, message: discord.Message):
    # Extract faction from author line (e.g. "Team Magma — Headquarters")
    embed = message.embeds[0] if message.embeds else None
    if not embed:
        return

    faction = None
    if not embed.author or not embed.author.name:
        return

    author_name = embed.author.name
    faction_match = re.search(r"Team (\w+)", author_name)
    if not faction_match:
        return

    faction = faction_match.group(1).lower()

    # Check if there is already a ball for that faction
    daily_ball_faction = daily_faction_ball_cache.get(faction)

    # Extract ball from embed description (e.g. "Your faction's daily ball-type is <:ball_emoji:ID> BallName")
    daily_ball = None
    if not embed.description:
        return

    ball_match = re.search(
        r"<:([a-zA-Z0-9_]+):\d+>\s+\*\*Today's target Pokemon are\*\*",
        embed.description,
    )
    if not ball_match:
        return

    daily_ball = ball_match.group(1).lower()

    # Update db and cache
    if daily_ball and daily_ball != daily_ball_faction:
        await update_faction_ball(bot, faction, daily_ball)

    member = await get_pokemeow_reply_member(message)
    if not member:
        return

    # Check if member is in faction members cache
    user_id = member.id
    faction_member = faction_members_cache.get(user_id)
    if not faction_member:
        return

    # Update faction if different
    faction_member_info = faction_members_cache.get(user_id)
    if faction_member_info:
        current_faction = faction_member_info.get("faction")
        if current_faction != faction:
            await update_faction_member_faction(bot, user_id, faction)

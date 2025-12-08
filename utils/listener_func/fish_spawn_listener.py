import re

import discord

from Constants.aesthetic import Emojis_Balls, Emojis_Factions
from Constants.faction_data import FACTION_LOGO_EMOJIS, get_faction_by_emoji
from Constants.vn_allstars_constants import VN_ALLSTARS_ROLES
from utils.cache.cache_list import (
    daily_faction_ball_cache,
    faction_members_cache,
    processed_fish_spawn_message_ids,
)
from utils.db.daily_faction_ball import update_faction_ball
from utils.db.faction_members import update_faction_member_faction
from utils.listener_func.pokemon_spawn_listener import (
    extract_trainer_name_from_description,
    faction_ball_alert,
    get_faction_member_via_trainer_name,
)
from utils.logs.debug_log import debug_log, enable_debug
from utils.logs.pretty_log import pretty_log
from utils.pokemeow.get_pokemeow_reply import get_pokemeow_reply_member

FISHING_COLOR = 0x87CEFA
from utils.logs.debug_log import debug_log, enable_debug

#enable_debug(f"{__name__}.fish_spawn_listener")


async def fish_spawn_listener(
    bot, before_message: discord.Message, after_message: discord.Message
):
    """Listener function to handle fish spawn events and faction ball alerts."""
    debug_log(
        f" Called for after_message.id: {getattr(after_message, 'id', None)} | bot: {getattr(bot, 'user', None)}"
    )
    embed = after_message.embeds[0] if after_message.embeds else None
    debug_log(f" Embed: {embed}")
    if not embed:
        debug_log(" No embed found, exiting.")
        return

    embed_description = embed.description or ""
    debug_log(f" Embed description: {embed_description}")
    if "fished a wild" not in embed_description:
        debug_log(
            " 'fished a wild' not in embed description, exiting."
        )
        return

    if after_message.id in processed_fish_spawn_message_ids:
        debug_log(
            f" Message ID {after_message.id} already processed, exiting."
        )
        return
    processed_fish_spawn_message_ids.add(after_message.id)

    guild = after_message.guild
    debug_log(f" Guild: {guild}")
    if not guild:
        debug_log(" No guild found, exiting.")
        return

    member = await get_pokemeow_reply_member(before_message)
    debug_log(f" Member from get_pokemeow_reply: {member}")
    if not member:
        trainer_name = extract_trainer_name_from_description(embed_description)
        debug_log(f" Trainer name extracted: {trainer_name}")
        if not trainer_name:
            debug_log(" No trainer name extracted, exiting.")
            return
        member = get_faction_member_via_trainer_name(bot, guild, trainer_name)
        debug_log(
            f" Member from get_faction_member_via_trainer_name: {member}"
        )
        if not member:
            debug_log(
                " No member found via trainer name, exiting."
            )
            return

    if "<:team_logo:" in embed_description:
        member_faction_info = faction_members_cache.get(member.id)
        debug_log(
            f" Faction member cache for {getattr(member, 'id', None)}: {member_faction_info}"
        )
        if not member_faction_info:
            debug_log(
                f" No faction member found in cache for {getattr(member, 'id', None)}, exiting."
            )
            return
        user_faction_notify = member_faction_info.get("notify")
        debug_log(f" user_faction_notify: {user_faction_notify}")

        if user_faction_notify and user_faction_notify.lower() != "off":
            debug_log(
                f" Notifying via faction_ball_alert for member {getattr(member, 'id', None)}."
            )
            await faction_ball_alert(member, before_message, after_message)

import re
import time

import discord

from utils.db.special_npc_timer_db_func import (
    fetch_ends_on_for_user_npc,
    get_special_battle_timer,
    upsert_special_battle_timer,
)
from utils.logs.debug_log import debug_log, enable_debug
from utils.logs.pretty_log import pretty_log
from utils.pokemeow.get_pokemeow_reply import get_pokemeow_reply_member

BATTLE_TIMER = 30 * 60  # 30 minutes in seconds

REACTION_EMOJI = "📅"

# Extracts the timestamp from a string like '<t:1766190355:R>'
enable_debug(f"{__name__}.special_battle_npc_timer_listener")


def extract_timestamp_from_message(content: str) -> int | None:
    """
    Extracts the integer timestamp from a Discord timestamp tag in the format <t:XXXXXXXXXX:R>.
    Returns the timestamp as an int if found, otherwise None.
    """
    match = re.search(r"<t:(\d+):[A-Za-z]>", content)
    if match:
        return int(match.group(1))
    return None


async def special_battle_npc_timer_listener(
    bot: discord.Client, message: discord.Message
):
    """Listens for special battle NPC timer messages and updates the database accordingly."""
    debug_log(
        f"special_battle_npc_timer_listener called. Message content: {message.content}"
    )
    member = await get_pokemeow_reply_member(message)
    if not member:
        debug_log("get_pokemeow_reply_member returned None.")
        pretty_log(
            "info",
            "special_battle_npc_timer_listener: Could not get member from Pokemeow reply.",
        )
        return

    user_id = member.id
    user_name = member.name
    channel_id = message.channel.id
    npc_name = "xmas_blue"
    debug_log(
        f"user_id={user_id}, user_name={user_name}, channel_id={channel_id}, npc_name={npc_name}"
    )

    # Extract timestamp
    ends_on = extract_timestamp_from_message(message.content)
    debug_log(f"Extracted ends_on timestamp: {ends_on}")
    if not ends_on:
        debug_log(
            f"Could not extract timestamp from message content: {message.content}"
        )
        pretty_log(
            "info",
            f"special_battle_npc_timer_listener: Could not extract timestamp from message content: {message.content}",
        )
        return

    debug_log(f"Fetching existing timer for user_id={user_id}, npc_name={npc_name}")
    existing_timer = await fetch_ends_on_for_user_npc(bot, user_id, "xmas_blue")
    debug_log(f"existing_timer={existing_timer}, ends_on={ends_on}")
    pretty_log(
        "info",
        f"special_battle_npc_timer_listener: existing_timer={existing_timer}, ends_on={ends_on} for user {user_name}, npc {npc_name}",
    )
    if existing_timer:
        # Check if different
        if existing_timer != ends_on:
            debug_log(f"existing_timer != ends_on, updating timer.")
            # Update the timer
            await upsert_special_battle_timer(
                bot, user_id, user_name, npc_name, ends_on, channel_id
            )
            debug_log(f"upsert_special_battle_timer called for update.")
            pretty_log(
                "info",
                f"Updated special battle timer for {user_name}, npc {npc_name}, ends_on {ends_on}",
            )
            await message.reference.resolved.add_reaction(REACTION_EMOJI)
        elif existing_timer == ends_on:
            debug_log(f"existing_timer == ends_on, no update needed.")
            pretty_log(
                "info",
                f"No update needed for special battle timer for {user_name}, npc {npc_name}, ends_on {ends_on}",
            )
    else:
        debug_log(f"No existing timer found, inserting new timer.")
        pretty_log(
            "info",
            f"No existing timer found for {user_name}, npc {npc_name}. Inserting new timer with ends_on {ends_on}",
        )
        # Insert new timer
        await upsert_special_battle_timer(
            bot, user_id, user_name, npc_name, ends_on, channel_id
        )
        debug_log(f"upsert_special_battle_timer called for insert.")
        await message.reference.resolved.add_reaction(REACTION_EMOJI)
        pretty_log(
            "info",
            f"Inserted new special battle timer for {user_name}, npc {npc_name}, ends_on {ends_on}",
        )


# 🍭 Listener for special battle NPC timers
async def special_battle_npc_listener(bot: discord.Client, message: discord.Message):

    member = await get_pokemeow_reply_member(message)
    if not member:
        return
    user_id = member.id
    user_name = str(member)

    channel_id = message.channel.id
    npc_name = "xmas_blue"

    # Ends on timestamp = now + BATTLE_TIMER
    ends_on = int(time.time()) + BATTLE_TIMER

    # Upsert the special battle timer
    await upsert_special_battle_timer(
        bot, user_id, user_name, npc_name, ends_on, channel_id
    )
    await message.reference.resolved.add_reaction(REACTION_EMOJI)

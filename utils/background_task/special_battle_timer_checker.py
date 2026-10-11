import time
from datetime import datetime

import discord

from Constants.timer_settings import BATTLE_EMOJI
from utils.db.special_npc_timer_db_func import (
    fetch_due_special_battle_timers, remove_special_battle_timer)
from utils.functions.retry_function import _retry_discord_call
from utils.logs.pretty_log import pretty_log


# 🍭 Helper function to fetch spooky_hour row
async def fetch_spooky_hour(bot: discord.Client):
    """
    Fetches the spooky_hour row if it is still active.
    Returns a dict with ends_on and message_id, or None if not found or already expired.
    """
    query = "SELECT ends_on, message_id FROM spooky_hour LIMIT 1"
    try:
        async with bot.pg_pool.acquire() as conn:
            row = await conn.fetchrow(query)
        if not row:
            return None

        ends_on = row["ends_on"]
        if isinstance(ends_on, datetime):
            ends_on = int(ends_on.timestamp())

        if ends_on <= int(time.time()):
            return None  # Spooky hour already ended; save Lusamine timers for next one

        return {"ends_on": ends_on, "message_id": row["message_id"]}
    except Exception as e:
        pretty_log(
            "error",
            f"Failed to fetch spooky_hour row: {e}",
        )
        return None


NPC_ID_MAP = {"alph_scientist": 970, "lusamine": 963}


# 🍭 Background task to check special battle timers
async def special_battle_timer_checker(bot: discord.Client):
    """Background task to check and notify about special battle timers."""

    # Fetch due special battle timers
    due_timers = await fetch_due_special_battle_timers(bot)
    if not due_timers:
        return  # No due timers

    # Check if spooky hour
    spooky_hour = await fetch_spooky_hour(bot)

    for timer in due_timers:
        user_id = timer["user_id"]
        npc_name = timer["npc_name"]
        channel_id = timer["channel_id"]

        if npc_name == "lusamine" and not spooky_hour:
            continue

        # Notify the user in the specified channel
        channel = bot.get_channel(channel_id)
        display_npc_name = npc_name.replace("_", " ").title()
        if channel:
            member = channel.guild.get_member(user_id)
            if member:
                # Remove timer from database
                content = f"{BATTLE_EMOJI} {member.mention}, you can now battle {display_npc_name} again!"
                npc_id = NPC_ID_MAP.get(npc_name, npc_name)
                desc = f";b npc {npc_id}"
                embed = discord.Embed(description=desc, color=0xC1B1A5)
                try:
                    await _retry_discord_call(
                        channel.send, content=content, embed=embed
                    )
                    pretty_log(
                        "info",
                        f"Notified {member.name} about special battle timer for npc {npc_name} and removed from database",
                    )
                    await remove_special_battle_timer(bot, user_id, npc_name)
                except Exception as e:
                    pretty_log(
                        "warn",
                        f"Failed to notify {member.name} for npc {npc_name}: {e}",
                    )
            else:
                await remove_special_battle_timer(bot, user_id, npc_name)
                pretty_log(
                    "warn",
                    f"Member not found in guild {channel.guild.id} for notifying about special battle timer for npc {npc_name}",
                )

        else:
            await remove_special_battle_timer(bot, user_id, npc_name)
            pretty_log(
                "warn",
                f"Channel {channel_id} not found for notifying about special battle timer for npc {npc_name}",
            )

import asyncio
import re
from datetime import datetime

import discord

from Constants.timer_settings import *
from utils.cache.cache_list import timer_cache  # 💜 import your cache
from utils.logs.pretty_log import pretty_log

# 🗂 Track scheduled "command ready" tasks to avoid duplicates
ready_tasks = {}
pokemon_ready_last_sent = {}
POKEMON_DEDUP_WINDOW_SECONDS = 5


async def _recent_duplicate_pokemon_ready_exists(
    channel: discord.abc.Messageable,
    bot_user_id: int,
    content: str,
) -> bool:
    """Check recent channel messages for identical pokemon-ready notifications."""
    now = discord.utils.utcnow()
    try:
        async for recent in channel.history(limit=10):
            if recent.author.id != bot_user_id:
                continue
            if recent.content != content:
                continue
            if (now - recent.created_at).total_seconds() <= 30:
                return True
    except Exception:
        return False
    return False


# 💜────────────────────────────────────────────
#   Function: detect_pokemeow_reply
#   Handles Pokemon timer notifications per user settings
# 💜────────────────────────────────────────────
async def pokemon_timer_handler(message: discord.Message):
    """
    Triggered on any message.
    Handles Pokemon ready notifications depending on user's timer cache settings:
      - off → ignore
      - on → ping them in channel
      - on w/o pings → send message w/o mention
      - react → ✅ react to PokeMeow's message
    """
    try:
        if message.author.id != POKEMEOW_APPLICATION_ID:
            return

        match = re.search(r"\*\*(.+?)\*\* found a wild", message.content)
        if not match:
            return

        username = match.group(1).strip()
        guild = message.guild

        # Match member case-insensitive
        member = discord.utils.find(
            lambda m: m.name.lower() == username.lower()
            or m.display_name.lower() == username.lower(),
            guild.members,
        )
        if not member:
            return

        # -------------------------------
        # 💜 Check timer_cache settings
        # -------------------------------
        user_settings = timer_cache.get(member.id)
        if not user_settings:
            return

        setting = (user_settings.get("pokemon_setting") or "off").lower()
        if setting == "off":
            return

        # Cancel previous ready task if any
        if member.id in ready_tasks and not ready_tasks[member.id].done():
            ready_tasks[member.id].cancel()

        # Schedule behavior depending on setting
        async def notify_ready():
            # 💜────────────────────────────────────────────
            #   Pokemon Timer Notification Task
            # 💜────────────────────────────────────────────
            try:
                await asyncio.sleep(POKEMON_TIMER)
                pretty_log(
                    tag="info",
                    message=f"Sending Pokemon timer ready notification to {member} (setting: {setting})",
                )
                if setting == "on":
                    content = f"{POKESPAWN_EMOJI} {member.mention}, your </pokemon:1015311085441654824> command is ready!"
                    dedup_key = (member.id, content)
                    now_ts = datetime.utcnow().timestamp()
                    last_sent_ts = pokemon_ready_last_sent.get(dedup_key, 0)
                    if now_ts - last_sent_ts < POKEMON_DEDUP_WINDOW_SECONDS:
                        return
                    if await _recent_duplicate_pokemon_ready_exists(
                        channel=message.channel,
                        bot_user_id=(
                            message.guild.me.id
                            if message.guild and message.guild.me
                            else 0
                        ),
                        content=content,
                    ):
                        return
                    pokemon_ready_last_sent[dedup_key] = now_ts
                    await message.channel.send(content)
                elif setting == "on w/o pings" or setting == "on_no_pings":
                    content = f"{POKESPAWN_EMOJI} **{member.name}**, your </pokemon:1015311085441654824> command is ready!"
                    dedup_key = (member.id, content)
                    now_ts = datetime.utcnow().timestamp()
                    last_sent_ts = pokemon_ready_last_sent.get(dedup_key, 0)
                    if now_ts - last_sent_ts < POKEMON_DEDUP_WINDOW_SECONDS:
                        return
                    if await _recent_duplicate_pokemon_ready_exists(
                        channel=message.channel,
                        bot_user_id=(
                            message.guild.me.id
                            if message.guild and message.guild.me
                            else 0
                        ),
                        content=content,
                    ):
                        return
                    pokemon_ready_last_sent[dedup_key] = now_ts
                    await message.channel.send(content)
                elif setting == "react":
                    await message.add_reaction(REACT_EMOJI)

            except asyncio.CancelledError:
                # 💙 [CANCELLED] Scheduled ready notification cancelled
                pretty_log(
                    tag="info",
                    message=f"Cancelled scheduled ready notification for {member}",
                )
            except Exception as e:
                # 💜 [MISSED] Timer ran correctly but message failed
                # Trackable: include member ID and username
                pretty_log(
                    tag="error",
                    message=(
                        f"Missed Pokemon timer notification for {member} "
                        f"(ID: {member.id}). Timer ran correctly but message failed: {e}"
                    ),
                )

        ready_tasks[member.id] = asyncio.create_task(notify_ready())

    except Exception as e:
        pretty_log(
            tag="critical",
            message=f"Unhandled exception in detect_pokemeow_reply: {e}",
        )

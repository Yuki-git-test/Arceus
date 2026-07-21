import asyncio
import re
from datetime import datetime

import discord

from Constants.timer_settings import *
from utils.cache.cache_list import timer_cache  # 💜 import your cache
from utils.cache.cache_list import timer_users
from utils.logs.debug_log import debug_log, enable_debug
from utils.logs.pretty_log import pretty_log

#enable_debug(f"{__name__}.pokemon_timer_handler")
#enable_debug(f"{__name__}.notify_ready")

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
            if (
                now - recent.created_at
            ).total_seconds() <= POKEMON_DEDUP_WINDOW_SECONDS:
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
        # debug_log(f"Received message from {message.author} (ID: {message.author.id}) | content: {message.content!r}")

        if message.author.id != POKEMEOW_APPLICATION_ID:
            debug_log(
                f"Skipping — author ID {message.author.id} != POKEMEOW_APPLICATION_ID {POKEMEOW_APPLICATION_ID}"
            )
            return

        match = re.search(r"\*\*(.+?)\*\* found a wild", message.content)
        if not match:
            debug_log(f"No regex match in content: {message.content!r}")
            return

        username = match.group(1).strip()
        debug_log(f"Regex matched username: {username!r}")
        guild = message.guild

        # Check timer_users cache first
        if username in timer_users:
            member = guild.get_member(timer_users[username])
            debug_log(f"Found member via cache: {member} (ID: {timer_users[username]})")
        else:
            # Match member case-insensitive and cache the result
            member = discord.utils.find(
                lambda m: m.name.lower() == username.lower()
                or m.display_name.lower() == username.lower(),
                guild.members,
            )
            if member:
                timer_users[username] = member.id
                debug_log(f"Found member via guild search: {member} (ID: {member.id})")
            else:
                debug_log(f"No member found for username {username!r} in guild {guild}")

        if not member:
            return

        # -------------------------------
        # 💜 Check timer_cache settings
        # -------------------------------
        user_settings = timer_cache.get(member.id)
        debug_log(f"timer_cache for {member} (ID: {member.id}): {user_settings}")
        if not user_settings:
            debug_log(f"No timer_cache entry for {member} — skipping")
            return

        setting = (user_settings.get("pokemon_setting") or "off").lower()
        debug_log(f"pokemon_setting for {member}: {setting!r}")
        if setting == "off":
            debug_log(f"Setting is 'off' — skipping")
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
                debug_log(
                    f"[notify_ready] Timer started for {member} (ID: {member.id}) | sleeping {POKEMON_TIMER}s"
                )
                await asyncio.sleep(POKEMON_TIMER)
                debug_log(
                    f"[notify_ready] Timer expired for {member} (ID: {member.id}) | setting: {setting!r}"
                )
                pretty_log(
                    tag="info",
                    message=f"Sending Pokemon timer ready notification to {member} (setting: {setting})",
                )
                if setting == "on":
                    content = f"{POKESPAWN_EMOJI} {member.mention}, your </pokemon:1015311085441654824> command is ready!"
                    dedup_key = (member.id, content)
                    now_ts = datetime.utcnow().timestamp()
                    last_sent_ts = pokemon_ready_last_sent.get(dedup_key, 0)
                    debug_log(
                        f"[notify_ready] Dedup check (on): now={now_ts:.1f} last_sent={last_sent_ts:.1f} diff={now_ts - last_sent_ts:.1f}s window={POKEMON_DEDUP_WINDOW_SECONDS}s"
                    )
                    if now_ts - last_sent_ts < POKEMON_DEDUP_WINDOW_SECONDS:
                        debug_log(
                            f"[notify_ready] Dedup blocked (in-memory) — skipping send for {member}"
                        )
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
                        debug_log(
                            f"[notify_ready] Dedup blocked (channel history) — skipping send for {member}"
                        )
                        return
                    debug_log(
                        f"[notify_ready] Sending 'on' message to channel {message.channel} (ID: {message.channel.id}) for {member}"
                    )
                    pokemon_ready_last_sent[dedup_key] = now_ts
                    try:
                        await message.channel.send(content)
                        debug_log(
                            f"[notify_ready] Sent 'on' message successfully for {member}"
                        )
                    except Exception as send_err:
                        debug_log(
                            f"[notify_ready] FAILED to send 'on' message for {member}: {send_err!r}",
                            highlight=True,
                        )
                elif setting == "on w/o pings" or setting == "on_no_pings":
                    content = f"{POKESPAWN_EMOJI} **{member.name}**, your </pokemon:1015311085441654824> command is ready!"
                    dedup_key = (member.id, content)
                    now_ts = datetime.utcnow().timestamp()
                    last_sent_ts = pokemon_ready_last_sent.get(dedup_key, 0)
                    debug_log(
                        f"[notify_ready] Dedup check (on_no_pings): now={now_ts:.1f} last_sent={last_sent_ts:.1f} diff={now_ts - last_sent_ts:.1f}s window={POKEMON_DEDUP_WINDOW_SECONDS}s"
                    )
                    if now_ts - last_sent_ts < POKEMON_DEDUP_WINDOW_SECONDS:
                        debug_log(
                            f"[notify_ready] Dedup blocked (in-memory) — skipping send for {member}"
                        )
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
                        debug_log(
                            f"[notify_ready] Dedup blocked (channel history) — skipping send for {member}"
                        )
                        return
                    debug_log(
                        f"[notify_ready] Sending 'on_no_pings' message to channel {message.channel} (ID: {message.channel.id}) for {member}"
                    )
                    pokemon_ready_last_sent[dedup_key] = now_ts
                    try:
                        await message.channel.send(content)
                        debug_log(
                            f"[notify_ready] Sent 'on_no_pings' message successfully for {member}"
                        )
                    except Exception as send_err:
                        debug_log(
                            f"[notify_ready] FAILED to send 'on_no_pings' message for {member}: {send_err!r}",
                            highlight=True,
                        )
                elif setting == "react":
                    debug_log(
                        f"[notify_ready] Adding react to message {message.id} for {member}"
                    )
                    await message.add_reaction(REACT_EMOJI)
                    debug_log(f"[notify_ready] React added successfully for {member}")

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

        debug_log(
            f"Scheduling notify_ready task for {member} (ID: {member.id}) | setting: {setting!r}"
        )
        ready_tasks[member.id] = asyncio.create_task(notify_ready())

    except Exception as e:
        pretty_log(
            tag="critical",
            message=f"Unhandled exception in detect_pokemeow_reply: {e}",
        )

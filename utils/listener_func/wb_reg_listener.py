import asyncio
import re
import time

import discord

from Constants.vn_allstars_constants import (
    ARCEUS_EMBED_COLOR,
    VN_ALLSTARS_EMOJIS,
    VN_ALLSTARS_TEXT_CHANNELS,
)
from utils.cache.cache_list import user_alerts_cache, vna_members_cache
from utils.logs.pretty_log import pretty_log
from utils.pokemeow.get_pokemeow_reply import (
    get_message_interaction_member,
    get_pokemeow_reply_member,
)

# Structure: {boss_name: {"time": unix_seconds, "users": set(user_ids), "task": asyncio.Task, "channels": {user_id: channel}}}
wb_tasks = {}


def extract_wb_unix_seconds(description: str) -> int | None:
    """
    Extracts the unix seconds from the line:
    '🔹 :crossed_swords: The battle begins <t:1763620682:R>'
    """
    match = re.search(r"<t:(\d+):R>", description)
    if match:
        return int(match.group(1))
    return None


def extract_wb_boss_name(description: str) -> str | None:
    """
    Extracts the boss name from the line:
    '🔹 :crossed_swords: Boss challenge: ... Shiny Gigantamax-Copperajah'
    """
    match = re.search(r"Boss challenge: [^>]+>\s*(.+)", description)
    if match:

        boss_name = match.group(1).strip()
        if "Shiny Gigantamax" in boss_name:
            boss_name = boss_name.replace(
                "Shiny Gigantamax-", f"{VN_ALLSTARS_EMOJIS.vna_shinygmax} "
            )
        elif "Gigantamax" in boss_name:
            boss_name = boss_name.replace(
                "Gigantamax-", f"{VN_ALLSTARS_EMOJIS.vna_gmax} "
            )
        elif "Shiny Eternamax" in boss_name:
            boss_name = boss_name.replace(
                "Shiny Eternamax-", f"{VN_ALLSTARS_EMOJIS.vna_shinygmax} "
            )
        elif "Eternamax" in boss_name:
            boss_name = boss_name.replace(
                "Eternamax-", f"{VN_ALLSTARS_EMOJIS.vna_gmax} "
            )

        return boss_name
    return None


async def world_boss_waiter(
    bot: discord.Client,
    unix_seconds,
    channel: discord.TextChannel,
    user: discord.User,
    wb_name: str,
):
    now = int(time.time())
    seconds_until_fight = unix_seconds - now
    if seconds_until_fight > 0:
        await asyncio.sleep(seconds_until_fight)
        task_info = wb_tasks.get(wb_name)
        if not task_info:
            return

        embed = discord.Embed(
            description=";wb f",
            color=ARCEUS_EMBED_COLOR,
        )
        embed.add_field(name="Iphone Copy:", value="`;wb f`", inline=False)
        for user_id in list(task_info["users"]):
            channel = task_info["channels"].get(user_id)
            user = bot.get_user(user_id)
            if not channel or not user:
                continue

            content = f"{user.mention}, You can now join the World Boss Battle for **{wb_name}**!"
            try:
                await channel.send(content=content, embed=embed)
                pretty_log(
                    "info",
                    f"Sent World Boss Battle reminder to user {user_id} in channel {channel.id}",
                )
            except Exception as e:
                pretty_log(
                    "error",
                    f"Failed to send World Boss Battle reminder to user {user_id} in channel {channel.id}: {e}",
                )

        # Clean up the task info
        wb_tasks.pop(wb_name, None)


async def start_world_boss_task(
    bot: discord.Client,
    unix_seconds,
    channel: discord.TextChannel,
    user: discord.User,
    wb_name: str,
    message: discord.Message,
):
    user_id = user.id

    # Subtract 5 seconds for early ping
    ping_time = unix_seconds - 5

    # Check if there's an existing task for this boss
    if wb_name in wb_tasks:
        task_info = wb_tasks[wb_name]

        # Check if user is already registered
        if user_id in task_info["users"]:
            pretty_log(
                "info",
                f"User {user_id} already registered for World Boss {wb_name} reminder.",
            )
            return
        # If the time is different, update it, else ignore
        if ping_time > task_info["time"]:
            task_info["time"] = ping_time
        task_info["users"].add(user_id)
        task_info["channels"][user_id] = channel
        pretty_log(
            "info",
            f"Added user {user_id} to existing World Boss {wb_name} reminder task.",
        )
        await message.add_reaction("📅")

    # No existing task, create a new one
    else:
        try:
            wb_tasks[wb_name] = {
                "time": ping_time,
                "users": set([user_id]),
                "channels": {user_id: channel},
                "task": asyncio.create_task(
                    world_boss_waiter(bot, ping_time, channel, user, wb_name)
                ),
            }
            await message.add_reaction("📅")
            pretty_log(
                "info",
                f"Created new World Boss {wb_name} reminder task for user {user_id}.",
            )
        except Exception as e:
            pretty_log(
                "error",
                f"Failed to create World Boss {wb_name} reminder task: {e}",
            )
            return


async def register_wb_battle_reminder(
    bot: discord.Client,
    message: discord.Message,
):
    """
    Register a world boss battle reminder for the user who sent the command.
    Extracts the boss name and unix seconds from the embed description.
    Stores the reminder in the database.
    """

    embed = message.embeds[0] if message.embeds else None
    if not embed or not embed.description:
        pretty_log("info", "No embed description found in the message.")
        return

    member = await get_pokemeow_reply_member(message)
    if not member:
        pretty_log(
            "info",
            "No replied member found for the message. Falling back to interaction.",
        )
        member = get_message_interaction_member(message)
        if not member:
            pretty_log("info", "No interaction member found. Cannot register reminder.")
            return

    # Check if their wb_battle alert is on
    from utils.cache.user_alert_cache import fetch_user_alert_notify_cache

    user_alert_setting = fetch_user_alert_notify_cache(
        user_id=member.id,
        alert_type="wb_battle",
    )
    if not user_alert_setting or user_alert_setting.lower() != "on":
        pretty_log(
            "info",
            f"User {member.id} has wb_battle alert off or not set. Skipping reminder registration.",
        )
        return
    guild = message.guild
    user_info = vna_members_cache.get(member.id)
    channel_id = user_info.get("channel_id") if user_info else None
    public_channel = guild.get_channel(VN_ALLSTARS_TEXT_CHANNELS.all_bots)
    notify_channel = None
    if not channel_id:
        # Fallback to public channel
        notify_channel = public_channel
    else:
        notify_channel = guild.get_channel(channel_id)
        if not notify_channel:
            notify_channel = public_channel

    unix_seconds = extract_wb_unix_seconds(embed.description)
    boss_name = extract_wb_boss_name(embed.description)

    now = int(time.time())
    if unix_seconds is None:
        pretty_log(
            "info",
            f"Failed to extract unix_seconds from embed description for message {message.id}. Skipping reminder registration.",
        )
        return
    seconds_until_fight = unix_seconds - now

    if boss_name and seconds_until_fight > 0:
        await start_world_boss_task(
            bot=bot,
            unix_seconds=unix_seconds,
            channel=notify_channel,
            user=member,
            wb_name=boss_name,
            message=message,
        )

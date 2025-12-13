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

wb_task = None


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
        content = (
            f"{user.mention}, You can now join the World Boss Battle for **{wb_name}**!"
        )
        embed = discord.Embed(
            description=";wb f",
            color=ARCEUS_EMBED_COLOR,
        )
        await channel.send(content=content, embed=embed)
        """# Remove the reminder after sending notification
        await remove_wb_reminder(bot, user.id)"""


async def start_world_boss_task(
    bot: discord.Client,
    unix_seconds,
    channel: discord.TextChannel,
    user: discord.User,
    wb_name: str,
    message: discord.Message,
):
    global wb_task
    # If a task is running and not done, don't start another
    if wb_task and not wb_task.done():
        pretty_log("info", "World boss reminder task already scheduled.")
        return
    await message.add_reaction("📅")
    wb_task = asyncio.create_task(
        world_boss_waiter(
            bot=bot,
            unix_seconds=unix_seconds,
            channel=channel,
            user=user,
            wb_name=wb_name,
        )
    )
    pretty_log("info", "World boss reminder task started.")


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
    seconds_until_fight = unix_seconds - now

    if unix_seconds and boss_name and seconds_until_fight > 0:
        await start_world_boss_task(
            bot=bot,
            unix_seconds=unix_seconds,
            channel=notify_channel,
            user=member,
            wb_name=boss_name,
            message=message,
        )

from datetime import datetime

import discord

from Constants.aesthetic import Emojis, Thumbnails
from Constants.vn_allstars_constants import VN_ALLSTARS_TEXT_CHANNELS
from utils.cache.cache_list import vna_members_cache
from utils.db.timezone_db import fetch_user_timezone
from utils.db.user_reminders_db import upsert_user_reminder
from utils.essentials.time_parsers import parse_remind_on, parse_repeat_interval
from utils.functions.webhook_func import send_webhook
from utils.logs.pretty_log import pretty_log
from utils.visuals.design_embed import design_embed
from utils.visuals.pretty_defer import pretty_defer


# 🌸───────────────────────────────────────────────🌸
# 🩷⏰  REMINDER CREATION FUNCTION                 🩷
# 🌸───────────────────────────────────────────────🌸
async def add_reminder_func(
    bot,
    interaction: discord.Interaction,
    message: str,
    remind_on: str,
    notify_type: str,
    repeat_interval: str = None,
):
    """Add reminder workflow using pretty_defer:
    - Immediate loader with safe edits
    - Updates steps live
    """
    # 🩷👤 Prepare user & loader
    user = interaction.user
    user_id = user.id
    user_name = user.name

    loader = await pretty_defer(
        interaction=interaction, content="Setting your reminder...", ephemeral=True
    )

    log_channel = interaction.guild.get_channel(VN_ALLSTARS_TEXT_CHANNELS.server_log)

    # ⏱ Parse remind_on
    tz_str = await fetch_user_timezone(bot=bot, user_id=user_id)
    if not tz_str:
        await loader.error(
            content="Please set your timezone first using /pong timezone"
        )
        return
    success, remind_on_ts, error_msg = parse_remind_on(remind_on, tz_str)
    if not success:
        await loader.error(content=f"{error_msg}")
        return

    # 🩷🔁 Parse repeat interval (optional)
    repeat_seconds = None
    if repeat_interval:
        success, repeat_seconds_or_error = parse_repeat_interval(repeat_interval)
        if not success:
            await loader.error(
                content=f"Invalid repeat interval: {repeat_seconds_or_error}"
            )
            return
        repeat_seconds = repeat_seconds_or_error

    target_channel = None
    if notify_type != "DM":
        vna_member_info = vna_members_cache.get(user_id)
        member_channel_id = (
            vna_member_info.get("channel_id") if vna_member_info else None
        )
        target_channel = (
            interaction.guild.get_channel(member_channel_id)
            if member_channel_id
            else None
        )
        if not target_channel:
            target_channel = VN_ALLSTARS_TEXT_CHANNELS.off_topic

    # 🩷💾 Insert reminder into DB
    try:
        await upsert_user_reminder(
            bot=bot,
            user_id=user_id,
            user_name=user_name,
            message=message,
            notify_type=notify_type,
            remind_on=remind_on_ts,
            repeat_interval=repeat_seconds,
            target_channel=target_channel.id if target_channel else None,
        )
    except Exception as e:
        await loader.error(content="Failed to set reminder.")
        pretty_log(
            tag="error",
            message=f"Failed to set reminder for {user_name} ({user_id}): {e}",
            include_trace=True,
        )
        return
    thumbnail_url = Thumbnails.pong

    # 🩷✅ Build confirmation embed
    embed = discord.Embed(
        title="Reminder set successfully",
        description=f"**Message:** {message}\n**Remind on:** <t:{remind_on_ts}:F>\n**Notify Type:** {notify_type}",
    )

    if repeat_seconds:
        embed.add_field(
            name=f"{Emojis.repeat_interval} Repeat Interval",
            value=f"{repeat_interval} ({repeat_seconds} seconds)",
            inline=True,
        )

    embed = design_embed(
        user=user,
        embed=embed,
        thumbnail_url=thumbnail_url,
    )

    # 🩷🎉 Send confirmation and log success
    await loader.success(embed=embed, content="Reminder set!")
    pretty_log(
        tag="success",
        message=f"Reminder set for {user_name} ({user_id}): '{message}' "
        f"Remind on <t:{remind_on_ts}:F> "
        f"{f'with repeat {repeat_interval}' if repeat_interval else ''} ",
    )

    # 🩷📝 Log to bot channel
    try:
        log_embed = discord.Embed(
            title=f"{Emojis.reminder} New Reminder Set",
            description=(
                f"- **Member:** {user.mention}\n"
                f"- **Message:** {message}\n"
                f"- **Remind on:** <t:{remind_on_ts}:F>\n"
                f"- **Notify Type:** {notify_type}\n"
                f"{f'- **Repeat Every:** {repeat_interval} ({repeat_seconds} seconds)\n' if repeat_seconds else ''}"
            ),
            timestamp=datetime.now(),
        )
        log_embed = design_embed(
            user=user, embed=log_embed, thumbnail_url=thumbnail_url
        )
        await send_webhook(
            bot=bot,
            channel=log_channel,
            embed=log_embed,
        )
    except Exception as e:
        pretty_log(
            tag="error",
            message=f"Failed to log reminder for {user_name} ({user_id}): {e}",
            include_trace=True,
        )

from datetime import datetime

import discord

from Constants.aesthetic import Thumbnails
from Constants.vn_allstars_constants import VN_ALLSTARS_TEXT_CHANNELS
from utils.cache.cache_list import vna_members_cache
from utils.db.timezone_db import fetch_user_timezone
from utils.db.user_reminders_db import fetch_user_reminder, update_user_reminder
from utils.essentials.time_parsers import parse_remind_on, parse_repeat_interval
from utils.functions.webhook_func import send_webhook
from utils.logs.pretty_log import pretty_log
from utils.visuals.design_embed import design_embed
from utils.visuals.pretty_defer import pretty_defer


# 🌸───────────────────────────────────────────────🌸
# 🩷⏰  REMINDER EDIT FUNCTION (USER REMINDER ID)  🩷
# 🌸───────────────────────────────────────────────🌸
async def edit_reminder_func(
    bot,
    interaction: discord.Interaction,
    reminder_id: str,
    new_message: str = None,
    new_remind_on: str = None,
    new_notify_type: str = None,
    new_repeat_interval: str = None,
):
    """Edit a user's reminder with confirmation and bot log embed."""

    user = interaction.user
    user_id = user.id
    user_name = user.name
    reminder_id = int(reminder_id)

    loader = await pretty_defer(
        interaction=interaction, content=f"Editing your reminder...", ephemeral=False
    )

    # Fetch existing reminder
    reminder = await fetch_user_reminder(bot, user_id, reminder_id)
    if not reminder:
        await loader.error(content="Invalid reminder ID.")
        return

    log_channel = interaction.guild.get_channel(VN_ALLSTARS_TEXT_CHANNELS.server_log)
    if not log_channel:
        await loader.error(content="Bot log channel not found.")
        return

    # Initialize optional vars
    new_remind_on_ts = None
    new_repeat_seconds = None

    # Parse remind_on
    if new_remind_on:
        tz_str = await fetch_user_timezone(bot=bot, user_id=user_id)
        if not tz_str:
            await loader.error(
                content="Please set your timezone first using /pong timezone"
            )
            return
        success, new_remind_on_ts, error_msg = parse_remind_on(new_remind_on, tz_str)
        if not success:
            await loader.error(content=f"{error_msg}")
            return

    # Parse repeat interval
    new_repeat_seconds = None
    if new_repeat_interval:
        success, repeat_seconds_or_error = parse_repeat_interval(new_repeat_interval)
        if not success:
            await loader.error(
                content=f"Invalid repeat interval: {repeat_seconds_or_error}"
            )
            return
        new_repeat_seconds = repeat_seconds_or_error

    target_channel = None
    if new_notify_type:
        if new_notify_type != "DM":
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
            target_channel = target_channel.id

    # Build dict of updated fields
    update_fields = {
        "message": new_message,
        "remind_on": new_remind_on_ts,
        "notify_type": new_notify_type,
        "repeat_interval": new_repeat_seconds,
        "target_channel": target_channel,
    }
    # Remove fields that are None to avoid overwriting existing values
    update_fields = {k: v for k, v in update_fields.items() if v is not None}

    # 🛑 Check if user actually updated something
    if not update_fields:
        await loader.error(
            content="You must update at least one field besides the reminder ID."
        )
        return
    try:
        await update_user_reminder(bot, user_id, reminder_id, update_fields)
    except Exception as e:
        await loader.error(content="❌ Failed to update reminder.")
        pretty_log(
            tag="error",
            message=f"Failed to update reminder {reminder_id} for {user_name} ({user_id}): {e}",
            include_trace=True,
        )
        return

    # 🩷✅ Build confirmation embed
    remind_on_value = new_remind_on_ts or reminder["remind_on"]

    embed = discord.Embed(
        title=f"🕗 Reminder ID: {reminder_id} Updated",
        description=(
            f"**Message:** {new_message or reminder['message']}\n"
            f"**Remind On:** <t:{int(remind_on_value)}:F>\n"
            f"**Notify Type:** {new_notify_type or reminder['notify_type']}\n"
        ),
        timestamp=datetime.now(),
    )

    # Add optional fields if present
    if new_repeat_seconds:
        embed.add_field(
            name="🕗 Repeat Interval",
            value=f"{new_repeat_interval} ({new_repeat_seconds} seconds)",
            inline=True,
        )

    thumbnail_url = Thumbnails.pong

    embed = design_embed(
        user=user,
        embed=embed,
        thumbnail_url=thumbnail_url,
    )

    # Send confirmation
    await loader.success(embed=embed, content="Reminder updated!")

    pretty_log(
        tag="success",
        message=f"Reminder {reminder_id} updated for {user_name} ({user_id})",
    )

    # Log to bot channel
    if log_channel:
        try:
            log_embed = discord.Embed(
                title=f"🕗 Reminder ID: {reminder_id} Updated",
                description=(
                    f"- **Member:** {user.mention}\n"
                    f"- **Message:** {new_message or reminder['message']}\n"
                    f"- **Remind On:** <t:{int(remind_on_value)}:F>\n"
                    f"**Notify Type:** {new_notify_type or reminder['notify_type']}\n"
                    f"{f'- **Repeat Every:** {new_repeat_interval} ({new_repeat_seconds} seconds)\n' if new_repeat_seconds else ''}"
                ),
                timestamp=datetime.now(),
            )
            log_embed = design_embed(
                user=user,
                embed=log_embed,
                thumbnail_url=thumbnail_url,
            )
            await send_webhook(
                bot=bot,
                channel=log_channel,
                embed=log_embed,
            )
        except Exception as e:
            pretty_log(
                tag="error",
                message=f"Failed to log reminder update for {user_name} ({user_id}): {e}",
                include_trace=True,
            )

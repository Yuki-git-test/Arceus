from datetime import datetime

import discord

from Constants.aesthetic import Thumbnails
from Constants.vn_allstars_constants import VN_ALLSTARS_TEXT_CHANNELS
from utils.db.user_reminders_db import (
    fetch_all_user_reminders,
    fetch_user_reminder,
    remove_all_user_reminders,
    remove_user_reminder,
)
from utils.essentials.time_parsers import format_repeats_on
from utils.functions.webhook_func import send_webhook
from utils.logs.pretty_log import pretty_log
from utils.visuals.design_embed import design_embed
from utils.visuals.pretty_defer import pretty_defer


# 🌸───────────────────────────────────────────────🌸
# 🩷 ⏰ REMOVE REMINDER FUNCTION WITH FULL EMBEDS   🩷
# 🌸───────────────────────────────────────────────🌸
async def remove_reminder_func(bot, interaction: discord.Interaction, reminder_id: str):
    """Remove reminder workflow with detailed embeds and bot log."""

    user = interaction.user
    user_id = user.id
    user_name = user.name

    all_reminders = False
    display_reminder_id = f"Reminder ID: {reminder_id}"

    reminder_id_str = str(reminder_id)
    if reminder_id_str.lower() == "all":
        display_reminder_id = "All Reminders"
        all_reminders = True

    loader = await pretty_defer(
        interaction=interaction,
        content=f"Removing {display_reminder_id}...",
        ephemeral=True,
    )

    log_channel = interaction.guild.get_channel(VN_ALLSTARS_TEXT_CHANNELS.server_log)

    if not all_reminders:
        # Fetch the single reminder
        reminder_id_int = int(reminder_id)  # safely convert string to int here
        reminder = await fetch_user_reminder(bot, user_id, reminder_id_int)
        if not reminder:
            await loader.error(content="Invalid reminder ID.")
            return

        # Remove the reminder
        await remove_user_reminder(bot, user_id, reminder_id_int)

        repeat_str = ""
        if reminder.get("repeat_interval"):
            repeat_str = f"**Repeat Every:** {format_repeats_on(reminder['repeat_interval'], compact=True)}"

        # Build embed showing deleted reminder
        embed = discord.Embed(
            title=f"🗑️ Removed Reminder {reminder_id_int}",
            description=(
                f"**Message:** {reminder['message']}\n"
                f"**Remind on:** <t:{int(reminder['remind_on'])}:F>\n"
                f"**Notify Type:** {reminder['notify_type'].title()}\n"
                f"{repeat_str}"
            ),
            timestamp=datetime.now(),
        )
        thumbnail_url = Thumbnails.pong

        embed = design_embed(
            user=user,
            embed=embed,
            thumbnail_url=thumbnail_url,
        )

        await loader.success(embed=embed, content="")

        pretty_log(
            tag="success",
            message=f"🗑️ Removed reminder {reminder_id_int} for {user_name} ({user_id})",
        )

        # Log to bot channel
        if log_channel:
            await send_webhook(
                bot=bot,
                channel=log_channel,
                embed=embed,
            )

    else:
        # Fetch all reminders
        reminders = await fetch_all_user_reminders(bot, user_id)
        if not reminders:
            await loader.error(content="You have no reminders to remove.")
            return

        # Remove all
        await remove_all_user_reminders(bot, user_id)

        # Build embed summarizing deleted reminders
        desc = ""
        for r in reminders[:10]:  # limit to 10 for embed size
            desc += f"**{r['user_reminder_id']}:  {r['message'][:20]}** — <t:{int(r['remind_on'])}:F>\n"
        if len(reminders) > 10:
            desc += f"...and {len(reminders)-10} more reminders.\n"

        embed = discord.Embed(
            title=f"🗑️ Removed All Reminders ({len(reminders)})",
            description=desc,
            timestamp=datetime.now(),
        )
        embed = design_embed(user=user, embed=embed, thumbnail_url=thumbnail_url)
        await loader.success(embed=embed, content="")

        pretty_log(
            tag="success",
            message=f"🗑️ Removed all {len(reminders)} reminders for {user_name} ({user_id})",
        )

        # Log to bot channel
        if log_channel:
            await send_webhook(
                bot=bot,
                channel=log_channel,
                embed=embed,
            )

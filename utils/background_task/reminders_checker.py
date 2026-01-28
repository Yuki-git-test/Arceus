# 🎉 loop_tasks/reminder_checker.py
from datetime import datetime

import discord

from Constants.vn_allstars_constants import VN_ALLSTARS_TEXT_CHANNELS, VNA_SERVER_ID
from utils.db.user_reminders_db import (
    fetch_due_reminders,
    remove_user_reminder,
    update_user_reminder,
)
from utils.logs.pretty_log import pretty_log


# 🐾────────────────────────────────────────────
#     ✨ Check & Trigger Due Reminders
#     Sends reminders whose time has passed
# 🐾────────────────────────────────────────────
async def check_and_trigger_reminders(bot):
    """Check due reminders and send them to the reminder channel.
    Repeats reminders if repeat_interval is set, otherwise deletes them.
    """
    reminders = await fetch_due_reminders(bot)
    if not reminders:
        return  # nothing to process
    guild = bot.get_guild(VNA_SERVER_ID)
    for r in reminders:
        try:
            # 📝 Make sure remind_on is a datetime (convert if stored as Unix int)
            remind_on = (
                datetime.fromtimestamp(r["remind_on"])
                if isinstance(r["remind_on"], (int, float))
                else r["remind_on"]
            )
            user_id = r["user_id"]
            user: discord.Member = guild.get_member(user_id) if guild else None
            if not user:
                await remove_user_reminder(bot, r["user_id"], r["user_reminder_id"])
                continue

            ping_text = f"{user.mention}"
            reminder_msg = f"{ping_text} ⏰ **Reminder:** {r['message']}"
            # 📤 Send the reminder
            notify_type = r["notify_type"]
            if notify_type == "Channel":
                reminder_channel_id = r.get("target_channel")
                reminder_channel = (
                    bot.get_channel(reminder_channel_id)
                    if reminder_channel_id
                    else None
                )
                if reminder_channel:
                    await reminder_channel.send(content=reminder_msg)
                else:
                    pretty_log(
                        tag="warn",
                        message=f"Target channel {reminder_channel_id} not found for user {user_id}, sending fallback",
                    )
                    off_topic = bot.get_channel(VN_ALLSTARS_TEXT_CHANNELS.off_topic)
                    if off_topic:
                        await off_topic.send(content=reminder_msg)
            else:
                # ✅ Try to DM first
                try:
                    dms = await user.create_dm()  # Ensure DM channel exists
                    await dms.send(content=reminder_msg)
                    pretty_log(
                        tag="ready",
                        message=f"💌 Successfully DM’d {user.display_name} ({user.id})",
                    )
                except discord.Forbidden:
                    pretty_log(
                        tag="info",
                        message=f"🛑 DMs blocked for {user.display_name} ({user.id}), using fallback channel",
                    )
                    off_topic = bot.get_channel(VN_ALLSTARS_TEXT_CHANNELS.off_topic)
                    if off_topic:
                        ping_text = f"{user.mention} 💌 I couldn't DM you, so here's your reminder!"
                        await off_topic.send(content=reminder_msg)

                    pretty_log(
                        tag="info",
                        message=(
                            f"⚠️ Reminder {r['user_reminder_id']} for {user.display_name} "
                            f"({user.id}) could not DM; sent to OffTopic instead."
                        ),
                    )
                except discord.HTTPException as e:
                    pretty_log(
                        tag="error",
                        message=f"❌ Failed to DM {user.display_name} ({user.id}): {e}",
                    )

            # 🔁 Handle repeat vs one-off
            if r.get("repeat_interval"):
                # If remind_on is datetime → convert to unix int before adding
                new_remind_on = (
                    int(remind_on.timestamp()) + int(r["repeat_interval"])
                    if isinstance(remind_on, datetime)
                    else int(remind_on) + int(r["repeat_interval"])
                )

                await update_user_reminder(
                    bot,
                    r["user_id"],
                    r["user_reminder_id"],
                    {"remind_on": new_remind_on},  # always int
                )
                pretty_log(
                    tag="success",
                    message=(
                        f"🔁 Repeated reminder {r['user_reminder_id']} for user {r['user_id']}, "
                        f"next at <t:{new_remind_on}:F>"
                    ),
                )
            else:
                await remove_user_reminder(bot, r["user_id"], r["user_reminder_id"])
                pretty_log(
                    tag="success",
                    message=(
                        f"🗑️ One-off reminder {r['user_reminder_id']} sent and deleted "
                        f"for user {r['user_id']}"
                    ),
                )

        except Exception as e:
            pretty_log(
                tag="error",
                message=(
                    f"Failed to send/process reminder {r['user_reminder_id']} "
                    f"for user {r['user_id']}: {e}"
                ),
                include_trace=True,
            )

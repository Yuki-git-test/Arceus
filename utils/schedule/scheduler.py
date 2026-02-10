import zoneinfo
from datetime import datetime
from zoneinfo import ZoneInfo

from utils.logs.pretty_log import pretty_log
from utils.schedule.schedule_helper import SchedulerManager

NYC = zoneinfo.ZoneInfo("America/New_York")  # auto-handles EST/EDT

# 🛠️ Create a SchedulerManager instance with Asia/Manila timezone
scheduler_manager = SchedulerManager(timezone_str="Asia/Manila")

# 🍥──────────────────────────────────────────────
# Scheduled Tasks Imports
# 🍥──────────────────────────────────────────────
from utils.schedule.daily_faction_ball_reset import daily_ball_reset
from utils.schedule.daily_ping import send_clan_wars_sub_reset_msg, send_daily_ping
from utils.schedule.goal_track_reset import (
    monthly_goal_track_reset,
    weekly_goal_track_reset,
)
from utils.schedule.os_lotto_ping import send_lotto_reminder


def format_next_run_manila(next_run_time):
    """
    Converts a timezone-aware datetime to Asia/Manila time and returns a readable string.
    """
    if next_run_time is None:
        return "No scheduled run time."
    # Convert to Manila timezone
    manila_tz = ZoneInfo("Asia/Manila")
    manila_time = next_run_time.astimezone(manila_tz)
    # Format as: Sunday, Nov 3, 2025 at 12:00 PM (Asia/Manila)
    return manila_time.strftime("%A, %b %d, %Y at %I:%M %p (Asia/Manila)")


# 🌈─────────────────────────────────────────────────────────────
# 💙 Minccino Scheduler Setup (setup_scheduler)
# 🌈─────────────────────────────────────────────────────────────
async def setup_scheduler(bot):

    # Start the scheduler
    scheduler_manager.start()
    # ✨─────────────────────────────────────────────────────────
    # 🤍 DAILY FACTION BALL RESET — Every Midnight (NYC)
    # ✨─────────────────────────────────────────────────────────
    try:
        daily_faction_ball_reset_job = scheduler_manager.add_cron_job(
            daily_ball_reset,
            "daily_faction_ball_reset",
            hour=0,
            minute=0,
            args=[bot],
            timezone=NYC,
        )
        readable_next_run = format_next_run_manila(
            daily_faction_ball_reset_job.next_run_time
        )
        pretty_log(
            tag="schedule",
            message=f"Daily faction ball reset job scheduled at {readable_next_run}",
            bot=bot,
        )
    except Exception as e:
        pretty_log(
            tag="error",
            message=f"Failed to schedule daily faction ball reset job: {e}",
            bot=bot,
        )
    # ✨─────────────────────────────────────────────────────────
    # 🤍 DAILY PING MESSAGE — Every 12 AM EST
    # ✨─────────────────────────────────────────────────────────
    try:
        daily_ping_job = scheduler_manager.add_cron_job(
            send_daily_ping,
            "daily_ping_message",
            hour=0,
            minute=0,
            args=[bot],
            timezone=NYC,
        )
        readable_next_run = format_next_run_manila(daily_ping_job.next_run_time)
        pretty_log(
            tag="schedule",
            message=f"Daily ping message job scheduled at {readable_next_run}",
            bot=bot,
        )
    except Exception as e:
        pretty_log(
            tag="error",
            message=f"Failed to schedule daily ping message job: {e}",
            bot=bot,
        )
    # ✨─────────────────────────────────────────────────────────
    # 🎯 Lotto Reminder — 10 mins before lottery draw (8:50 PM New York time)
    # ✨─────────────────────────────────────────────────────────
    try:
        lotto_reminder_job = scheduler_manager.add_cron_job(
            send_lotto_reminder,
            "os_lotto_reminder",
            hour=20,
            minute=50,
            args=[bot],
            timezone=NYC,
        )
        readable_next_run = format_next_run_manila(lotto_reminder_job.next_run_time)
        pretty_log(
            tag="schedule",
            message=f"OS Lotto reminder job scheduled at {readable_next_run}",
            bot=bot,
        )
    except Exception as e:
        pretty_log(
            tag="error",
            message=f"Failed to schedule OS Lotto reminder job: {e}",
            bot=bot,
        )
    # ✨─────────────────────────────────────────────────────────
    # 🎯 Weekly Goal Tracker Reset Every Sunday at Midnight EST
    # ✨─────────────────────────────────────────────────────────
    try:
        weekly_goal_reset_job = scheduler_manager.add_cron_job(
            weekly_goal_track_reset,
            "weekly_goal_tracker_reset",
            day_of_week="sun",
            hour=0,
            minute=0,
            args=[bot],
            timezone=NYC,
        )
        readable_next_run = format_next_run_manila(weekly_goal_reset_job.next_run_time)
        pretty_log(
            tag="schedule",
            message=f"Weekly goal tracker reset job scheduled at {readable_next_run}",
            bot=bot,
        )
    except Exception as e:
        pretty_log(
            tag="error",
            message=f"Failed to schedule weekly goal tracker reset job: {e}",
            bot=bot,
        )
    # ✨─────────────────────────────────────────────────────────
    # 🎯 Monthly Goal Tracker Reset — 1st of the Month at Midnight EST
    # ✨─────────────────────────────────────────────────────────
    try:
        monthly_goal_reset_job = scheduler_manager.add_cron_job(
            monthly_goal_track_reset,
            "monthly_goal_tracker_reset",
            day_of_month=1,
            hour=0,
            minute=0,
            args=[bot],
            timezone=NYC,
        )
        readable_next_run = format_next_run_manila(monthly_goal_reset_job.next_run_time)
        pretty_log(
            tag="schedule",
            message=f"Monthly goal tracker reset job scheduled at {readable_next_run}",
            bot=bot,
        )
    except Exception as e:
        pretty_log(
            tag="error",
            message=f"Failed to schedule monthly goal tracker reset job: {e}",
            bot=bot,
        )

    # ✨─────────────────────────────────────────────────────────
    # 🎯 Clan Wars Sub Reset Ping — Everyday at 12:00 AM Est
    # ✨─────────────────────────────────────────────────────────
    try:
        clan_wars_sub_reset_job = scheduler_manager.add_cron_job(
            send_clan_wars_sub_reset_msg,
            "clan_wars_sub_reset_ping",
            hour=0,
            minute=0,
            args=[bot],
            timezone=NYC,
        )
        readable_next_run = format_next_run_manila(
            clan_wars_sub_reset_job.next_run_time
        )
        pretty_log(
            tag="schedule",
            message=f"Clan Wars sub reset ping job scheduled at {readable_next_run}",
            bot=bot,
        )
    except Exception as e:
        pretty_log(
            tag="error",
            message=f"Failed to schedule Clan Wars sub reset ping job: {e}",
            bot=bot,
        )

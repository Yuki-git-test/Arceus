import zoneinfo
from datetime import datetime
from zoneinfo import ZoneInfo

from utils.logs.pretty_log import pretty_log
from utils.schedule.daily_faction_ball_reset import daily_ball_reset
from utils.schedule.schedule_helper import SchedulerManager

NYC = zoneinfo.ZoneInfo("America/New_York")  # auto-handles EST/EDT

# 🛠️ Create a SchedulerManager instance with Asia/Manila timezone
scheduler_manager = SchedulerManager(timezone_str="Asia/Manila")


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

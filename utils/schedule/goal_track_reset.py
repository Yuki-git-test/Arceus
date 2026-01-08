import discord

from utils.db.monthly_goal_tracker import delete_all_monthly_goals
from utils.db.weekly_goal_tracker import delete_all_weekly_goals
from utils.logs.pretty_log import pretty_log

# 🍥──────────────────────────────────────────────
# Weekly Goal Tracker Reset Task
# 🍥──────────────────────────────────────────────
async def weekly_goal_track_reset(bot):
    """Resets the weekly goal tracker data."""
    try:
        await delete_all_weekly_goals(bot)
        pretty_log(
            tag="background_task",
            message="Weekly goal tracker data has been reset.",
            bot=bot,
        )
    except Exception as e:
        pretty_log(
            tag="error",
            message=f"Failed to reset weekly goal tracker data: {e}",
            bot=bot,
        )

# 🍥──────────────────────────────────────────────
# Monthly Goal Tracker Reset Task
# 🍥──────────────────────────────────────────────
async def monthly_goal_track_reset(bot):
    """Resets the monthly goal tracker data."""
    try:
        await delete_all_monthly_goals(bot)
        pretty_log(
            tag="background_task",
            message="Monthly goal tracker data has been reset.",
            bot=bot,
        )
    except Exception as e:
        pretty_log(
            tag="error",
            message=f"Failed to reset monthly goal tracker data: {e}",
            bot=bot,
        )
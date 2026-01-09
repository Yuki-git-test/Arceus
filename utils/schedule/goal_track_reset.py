import discord

from Constants.vn_allstars_constants import VN_ALLSTARS_TEXT_CHANNELS, VNA_SERVER_ID
from utils.db.monthly_goal_tracker import delete_all_monthly_goals
from utils.db.weekly_goal_tracker import delete_all_weekly_goals
from utils.logs.pretty_log import pretty_log

NEW_WEEK_IMAGE_URL = "https://media.discordapp.net/attachments/1459004743295963206/1459008048709501039/new_week.png?ex=6961b6a1&is=69606521&hm=167345643b517350b7d11d2b5bee37191529cad9dfad67497bdd72d024c98e50&=&format=webp&quality=lossless&width=762&height=256"
NEW_MONTH_IMAGE_URL = "https://media.discordapp.net/attachments/1459004743295963206/1459008027293253764/new_month.png?ex=6961b69c&is=6960651c&hm=a95a0cd2eab9560b29a52581ef4d5f9dbd35216d0817c0eac2199b22c6366508&=&format=webp&quality=lossless&width=762&height=256"
GOAL_TRACKER_CHANNEL_ID = VN_ALLSTARS_TEXT_CHANNELS.goal_tracker


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
        # Send notification to Goal Tracker channel
        guild = bot.get_guild(VNA_SERVER_ID)
        if guild:
            channel = guild.get_channel(GOAL_TRACKER_CHANNEL_ID)
            if channel:
                await channel.send(NEW_WEEK_IMAGE_URL)

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
        # Send notification to Goal Tracker channel
        guild = bot.get_guild(VNA_SERVER_ID)
        if guild:
            channel = guild.get_channel(GOAL_TRACKER_CHANNEL_ID)
            if channel:
                await channel.send(NEW_MONTH_IMAGE_URL)
                
    except Exception as e:
        pretty_log(
            tag="error",
            message=f"Failed to reset monthly goal tracker data: {e}",
            bot=bot,
        )

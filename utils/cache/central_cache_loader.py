import discord

from utils.logs.pretty_log import pretty_log

from .cache_list import market_alert_cache
from .clan_wars_cache import load_clan_wars_server_members_cache
from .daily_fa_ball_cache import load_daily_faction_ball_cache
from .faction_members_cache import load_faction_members_cache
from .market_alert_cache import load_market_alert_cache
from .monthly_goal_tracker_cache import load_monthly_goal_cache
from .ping_message_id_cache import load_ping_message_id_cache
from .timers_cache import load_timer_cache
from .user_alert_cache import load_user_alert_cache
from .vna_members_cache import load_vna_members_cache
from .webhook_url_cache import load_webhook_url_cache
from .weekly_goal_tracker_cache import load_weekly_goal_cache
from utils.db.market_value_db import load_market_cache_from_db

async def load_all_cache(bot: discord.Client):
    """
    Loads all caches used by the bot.
    Currently loads:
    - Market Alert Cache
    """
    try:
        # Load VNA Members Cache
        await load_vna_members_cache(bot)

        # Load Ping Message ID Cache
        await load_ping_message_id_cache(bot)

        # Load Weekly Goal Cache
        await load_weekly_goal_cache(bot)

        # Load Monthly Goal Cache
        await load_monthly_goal_cache(bot)

        # Load Clan Wars Server Members Cache
        await load_clan_wars_server_members_cache(bot)

        # Load Timer Cache
        await load_timer_cache(bot)

        # Load Market Alert Cache
        await load_market_alert_cache(bot)

        # Load Webhook URL Cache
        await load_webhook_url_cache(bot)

        # Load Faction Members Cache
        await load_faction_members_cache(bot)

        # Load Daily Faction Ball Cache
        await load_daily_faction_ball_cache(bot)

        # Load User Alert Cache
        await load_user_alert_cache(bot)

        # Load Market Value Cache from database
        await load_market_cache_from_db(bot)

    except Exception as e:
        pretty_log(
            message=f"❌ Error loading caches: {e}",
            tag="cache",
        )
        return
    pretty_log(
        message="✅ All caches loaded successfully.",
        tag="cache",
    )

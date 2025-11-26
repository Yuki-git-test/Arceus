import discord

from utils.logs.pretty_log import pretty_log

from .cache_list import market_alert_cache
from .market_alert_cache import load_market_alert_cache

async def load_all_cache(bot: discord.Client):
    """
    Loads all caches used by the bot.
    Currently loads:
    - Market Alert Cache
    """
    try:
        await load_market_alert_cache(bot)

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
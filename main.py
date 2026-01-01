# from keep_alive import keep_alive
import asyncio
import os

import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv

from utils.cache.central_cache_loader import load_all_cache
from utils.db.get_pg_pool import get_pg_pool
from utils.listener_func.market_feed_listener import (
    processed_market_feed_ids,
    processed_market_feed_message_ids,
)
from utils.logs.pretty_log import pretty_log, set_arceus_bot
from utils.schedule.scheduler import setup_scheduler
from utils.cache.cache_list import clear_processed_messages_cache
from utils.essentials.persist_views import register_persistent_views
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True
load_dotenv()

# 🟣────────────────────────────────────────────
#            ⚡ Initialize Bot Instance ⚡
# 🟣────────────────────────────────────────────
bot = commands.Bot(command_prefix="!", intents=discord.Intents.all(), help_command=None)
set_arceus_bot(bot=bot)


# 🟣────────────────────────────────────────────
#         ⚡ Hourly Cache Refresh Task ⚡
# 🟣────────────────────────────────────────────
@tasks.loop(hours=1)
async def refresh_all_caches():

    # Removed first-run skip logic so cache loads immediately
    await load_all_cache(bot)

    # Clear processed message ID sets to prevent memory bloat
    clear_processed_messages_cache()


# 🟣────────────────────────────────────────────
#          ⚡ Load Extensions Dynamically ⚡
# 🟣────────────────────────────────────────────
async def load_extensions():
    """
    Dynamically load all Python files in the 'cogs' folder (ignores __pycache__).
    Logs loaded cogs with pretty_log and errors if loading fails.
    """
    loaded_cogs = []
    for root, dirs, files in os.walk("cogs"):
        # Skip __pycache__ folders
        dirs[:] = [d for d in dirs if d != "__pycache__"]

        for file in files:
            if file.endswith(".py") and not file.startswith("__"):
                module_path = (
                    os.path.join(root, file).replace(os.sep, ".").replace(".py", "")
                )
                try:
                    await bot.load_extension(module_path)
                    loaded_cogs.append(module_path)
                except Exception as e:
                    pretty_log(
                        message=f"❌ Failed to load cog: {module_path}\n{e}",
                        tag="error",
                    )
    _loaded_count = len(loaded_cogs)
    pretty_log("ready", f"✅ Loaded { _loaded_count} cogs")
    # ----------------- Keep your commented-out cogs -----------------
    # await bot.load_extension("cogs.currency")
    # await bot.load_extension("cogs.library")
    # await bot.load_extension("cogs.application")
    # -----------------------------------------------------------------


# 🟣────────────────────────────────────────────
#              ⚡ On Ready Event ⚡
# 🟣────────────────────────────────────────────
@bot.event
async def on_ready():
    pretty_log(message=f"✅ Logged in as {bot.user}", tag="ready")

    # Sync all slash commands globally
    await bot.tree.sync()
    commands_count = len(bot.tree.get_commands())
    pretty_log(
        message=f"✅ Synced {commands_count} slash commands globally", tag="ready"
    )

    # Start the hourly cache refresh task
    if not refresh_all_caches.is_running():
        refresh_all_caches.start()
        pretty_log(message="✅ Started hourly cache refresh task", tag="ready")


# 🟣────────────────────────────────────────────
#               ⚡ Main Entry Point ⚡
# 🟣────────────────────────────────────────────
async def main():
    # keep_alive()  # Start the Replit Flask server
    await load_extensions()
    # Intialize the database pool
    try:
        bot.pg_pool = await get_pg_pool()
        pretty_log(message="✅ PostgreSQL connection pool established", tag="ready")
    except Exception as e:
        pretty_log(
            tag="critical",
            message=f"Failed to initialize database pool: {e}",
            include_trace=True,
        )
        return  # Exit if DB connection fails

    # Start the scheduler
    await setup_scheduler(bot)

    # Register persistent views
    await register_persistent_views(bot)
    
    # Start the bot
    token = os.getenv("DISCORD_TOKEN")
    await bot.start(token)


# 🟣────────────────────
#   🚀 Start Bot 🚀
# 🟣────────────────────
asyncio.run(main())

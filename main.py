import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from utils.logs.pretty_log import pretty_log, set_arceus_bot

# from keep_alive import keep_alive
import asyncio

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True
load_dotenv()
bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())
set_arceus_bot(bot=bot)

# 🟣────────────────────────────────────────────
#          ⚡ Load Extensions Dynamically ⚡
# 🟣────────────────────────────────────────────
async def load_extensions():
    """
    Dynamically load all Python files in the 'cogs' folder (ignores __pycache__).
    Logs loaded cogs with pretty_log and errors if loading fails.
    """
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
                    pretty_log(message=f"✅ Loaded cog: {module_path}", tag="ready")
                except Exception as e:
                    pretty_log(
                        message=f"❌ Failed to load cog: {module_path}\n{e}", tag="error"
                    )

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
    pretty_log(message="Commands loaded:", tag="ready")

    # Regular prefix commands
    for cmd in bot.commands:
        pretty_log(message=f"- {cmd.name} (prefix)", tag="cmd")

    # Slash commands
    for cmd in bot.tree.walk_commands():
        pretty_log(message=f"- {cmd.name} (slash)", tag="cmd")


# 🟣────────────────────────────────────────────
#               ⚡ Main Entry Point ⚡
# 🟣────────────────────────────────────────────
async def main():
    # keep_alive()  # Start the Replit Flask server
    await load_extensions()
    token = os.getenv("DISCORD_TOKEN")
    await bot.start(token)


# 🟣────────────────────
#   🚀 Sttrt Bot 🚀
# 🟣────────────────────
asyncio.run(main())

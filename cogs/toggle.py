import discord
from discord import app_commands
from discord.ext import commands
from typing import Literal, Optional

from utils.essentials.command_safe import run_command_safe
from utils.group_command_func.toggle import *

from utils.logs.pretty_log import pretty_log

# 🍭──────────────────────────────
#   🎀 Toggle Group Command
# 🍭──────────────────────────────
class Toggle_Group_Command(commands.Cog):
    """
    Group command for toggling various features.
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    toggle = app_commands.Group(
        name="toggle",
        description="Toggle various features on or off.",
    )

    # 🍭──────────────────────────────
    #   🎀 /toggle alerts
    # 🍭──────────────────────────────
    @toggle.command(
        name="alerts",
        description="Toggle alerts on or off.",
    )
    async def toggle_alerts(
        self,
        interaction: discord.Interaction,
    ):
        slash_cmd_name = "toggle alerts"
        await run_command_safe(
            bot=self.bot,
            interaction=interaction,
            command_func=alert_settings_func,
            slash_cmd_name=slash_cmd_name,
        )
        
    toggle_alerts.extras = {"category": "Public"}
async def setup(bot: commands.Bot):
    await bot.add_cog(Toggle_Group_Command(bot))
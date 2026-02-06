from typing import Literal

import discord
from discord import app_commands
from discord.ext import commands

from utils.essentials.command_safe import run_command_safe
from utils.group_command_func.clan_wars_trophies import *


# 🐾────────────────────────────────────────────
#     🎐 Clan Wars Trophies Command Group Cog
# 🐾────────────────────────────────────────────
class TrophiesCommandGroup(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # ⚡ Top-level group (only register once!)
    trophy_group = app_commands.Group(
        name="trophy",
        description="Clan Wars Trophies related commands",
    )

    # 🎀────────────────────────────────────────────
    #           🌸 /trophy multi 🌸
    # 🎀────────────────────────────────────────────
    @trophy_group.command(
        name="multi",
        description="Add or remove trophies for multiple clans at once",
    )
    @app_commands.describe(
        action="Whether to add or remove trophies",
        amount="The amount of trophies to add or remove",
        clan1="The first clan (required)",
        clan2="The second clan (optional)",
        clan3="The third clan (optional)",
        clan4="The fourth clan (optional)",
        clan5="The fifth clan (optional)",
        clan6="The sixth clan (optional)",
        clan7="The seventh clan (optional)",
        clan8="The eighth clan (optional)",
        clan9="The ninth clan (optional)",
        clan10="The tenth clan (optional)",
    )
    @app_commands.checks.has_permissions(
        administrator=True
    )  # Only allow administrators to use this command
    async def trophy_multi(
        self,
        interaction: discord.Interaction,
        action: Literal["add", "remove"],
        amount: int,
        clan1: discord.Role,
        clan2: discord.Role = None,
        clan3: discord.Role = None,
        clan4: discord.Role = None,
        clan5: discord.Role = None,
        clan6: discord.Role = None,
        clan7: discord.Role = None,
        clan8: discord.Role = None,
        clan9: discord.Role = None,
        clan10: discord.Role = None,
    ):

        await run_command_safe(
            bot=self.bot,
            interaction=interaction,
            slash_cmd_name="trophy multi",
            command_func=trophy_multi_func,
            action=action,
            amount=amount,
            clan1=clan1,
            clan2=clan2,
            clan3=clan3,
            clan4=clan4,
            clan5=clan5,
            clan6=clan6,
            clan7=clan7,
            clan8=clan8,
            clan9=clan9,
            clan10=clan10,
        )

    trophy_multi.extras = {"category": "Staff"}

    # 🎀────────────────────────────────────────────
    #           🌸 /trophy reset 🌸
    # 🎀────────────────────────────────────────────
    @trophy_group.command(
        name="reset",
        description="Reset all clan wars trophies (staff only)",
    )
    @app_commands.checks.has_permissions(
        administrator=True
    )  # Only allow administrators to use this command
    async def trophy_reset(self, interaction: discord.Interaction):
        await run_command_safe(
            bot=self.bot,
            interaction=interaction,
            slash_cmd_name="trophy reset",
            command_func=reset_trophies_func,
        )

    trophy_reset.extras = {"category": "Staff"}

    # 🎀────────────────────────────────────────────
    #           🌸 /trophy leaderboard 🌸
    # 🎀────────────────────────────────────────────
    @trophy_group.command(
        name="leaderboard",
        description="View the current clan wars trophies leaderboard",
    )
    async def trophy_leaderboard(self, interaction: discord.Interaction):
        await run_command_safe(
            bot=self.bot,
            interaction=interaction,
            slash_cmd_name="trophy leaderboard",
            command_func=view_leaderboard_func,
        )

    trophy_leaderboard.extras = {"category": "Public"}

# 🐾────────────────────────────────────────────
#     🎐 Setup Function
# 🐾────────────────────────────────────────────
async def setup(bot: commands.Bot):
    await bot.add_cog(TrophiesCommandGroup(bot))
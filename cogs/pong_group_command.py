# 🐾────────────────────────────────────────────
#     🎐 Coll Command Group
# 🐾────────────────────────────────────────────
from typing import Literal

import discord
from discord import app_commands
from discord.ext import commands

from utils.db.timezone_db import tz_autocomplete
from utils.db.user_reminders_db import reminder_id_autocomplete
from utils.essentials.command_safe import run_command_safe
from utils.group_command_func.pong import *

desc = "Reminder commands"


# 🐾────────────────────────────────────────────
#     🎐 Coll Command Group Cog
# 🐾────────────────────────────────────────────
class ReminderCommandGroup(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # ⚡ Top-level group (only register once!)
    pong_group = app_commands.Group(
        name="pong",
        description=desc,
    )

    # 🤍💫────────────────────────────────────────────💫🤍
    #        🎐 Reminder Group Commands
    # 🤍💫────────────────────────────────────────────💫🤍
    # 🤍─────────────────────────────────────────────
    # 🪄 /pong timezone
    # 🤍─────────────────────────────────────────────
    @pong_group.command(
        name="timezone", description="Sets a member's timezone for reminders"
    )
    @app_commands.autocomplete(timezone=tz_autocomplete)
    async def reminder_set_timezone(
        self,
        interaction: discord.Interaction,
        timezone: str,
    ):

        await run_command_safe(
            bot=self.bot,
            interaction=interaction,
            slash_cmd_name="reminder timezone",
            command_func=reminder_set_timezone_func,
            timezone=timezone,
        )

    reminder_set_timezone.extras = {"category": "Public"}

    # 🎀────────────────────────────────────────────
    #           🌸 /pong add 🌸
    # 🎀────────────────────────────────────────────
    @pong_group.command(name="add", description="Adds a new reminder")
    @app_commands.describe(
        message="The message for your reminder",
        remind_on="When to be reminded (Valid format: 12/30 18:20 | 12h | 1d3m)",
        notify_type="DMs or Personal Channel (Off Topic if guest)",
        repeat_interval="Optional repeat interval (Valid format: 12h | 1d3m)",
    )
    async def add_reminder(
        self,
        interaction: discord.Interaction,
        message: str,
        remind_on: str,
        notify_type: Literal["Channel", "DM"],
        repeat_interval: str = None,
    ):

        slash_cmd_name = "pong add"

        await run_command_safe(
            bot=self.bot,
            interaction=interaction,
            slash_cmd_name=slash_cmd_name,
            command_func=add_reminder_func,
            message=message,
            remind_on=remind_on,
            notify_type=notify_type,
            repeat_interval=repeat_interval,
        )

    add_reminder.extras = {"category": "Public"}

    # 🎀────────────────────────────────────────────
    #           🌸 /pong remove 🌸
    # 🎀────────────────────────────────────────────
    @pong_group.command(
        name="remove",
        description="Removes an existing reminder by ID, or all reminders",
    )
    @app_commands.autocomplete(
        reminder_id=reminder_id_autocomplete
    )  # 👈 attach autocomplete
    @app_commands.describe(reminder_id="Reminder ID, or 'all' to remove all alerts")
    async def remove_reminder(self, interaction: discord.Interaction, reminder_id: str):

        slash_cmd_name = "pong remove"

        await run_command_safe(
            bot=self.bot,
            interaction=interaction,
            slash_cmd_name=slash_cmd_name,
            command_func=remove_reminder_func,
            reminder_id=reminder_id,
        )

    remove_reminder.extras = {"category": "Public"}

    # 🎀────────────────────────────────────────────
    #           🌸 /pong edit 🌸
    # 🎀────────────────────────────────────────────
    @pong_group.command(name="edit", description="Updates an existing reminder")
    @app_commands.autocomplete(reminder_id=reminder_id_autocomplete)
    @app_commands.describe(
        reminder_id="The ID of the reminder to edit",
        new_message="The new message for your reminder",
        new_remind_on="When to be reminded (Valid format: 12/30 18:20 | 12h | 1d3m)",
        new_notify_type="DMs or Personal Channel (Off Topic if guest)",
        new_repeat_interval="Optional new repeat interval (Valid format: 12h | 1d3m)",
    )
    async def edit_reminder(
        self,
        interaction: discord.Interaction,
        reminder_id: str,
        new_message: str = None,
        new_remind_on: str = None,
        new_notify_type: str = None,
        new_repeat_interval: str = None,
    ):

        slash_cmd_name = "pong edit"

        await run_command_safe(
            bot=self.bot,
            interaction=interaction,
            slash_cmd_name=slash_cmd_name,
            command_func=edit_reminder_func,
            reminder_id=reminder_id,
            new_message=new_message,
            new_remind_on=new_remind_on,
            new_repeat_interval=new_repeat_interval,
            new_notify_type=new_notify_type,
        )

    edit_reminder.extras = {"category": "Public"}

    # 🎀────────────────────────────────────────────
    #           🌸 /pong list 🌸
    # 🎀────────────────────────────────────────────
    @pong_group.command(name="list", description="List all your active reminders")
    async def list_reminder(self, interaction: discord.Interaction):

        slash_cmd_name = "pong list"

        await run_command_safe(
            bot=self.bot,
            interaction=interaction,
            slash_cmd_name=slash_cmd_name,
            command_func=reminders_list_func,
        )

    list_reminder.extras = {"category": "Public"}


# 💙✨────────────────────────────────────────────✨💙
#        ✨ Reminder Group Setup – Add Some Magic
# 💙✨────────────────────────────────────────────✨💙
async def setup(bot: commands.Bot):
    cog = ReminderCommandGroup(bot)
    await bot.add_cog(cog)
    pong_group = ReminderCommandGroup.pong_group  # top-level app_commands.Group

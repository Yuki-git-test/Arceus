SKIP_FIRST_GUILD = False  # Set to False to send to all guilds
import discord
from discord import app_commands
from discord.ext import commands

from Constants.aesthetic import Emojis
from Constants.vn_allstars_constants import ARCEUS_EMBED_COLOR, VNA_SERVER_ID, VN_ALLSTARS_TEXT_CHANNELS, YUKI_USER_ID, KHY_USER_ID

from utils.functions.webhook_func import send_webhook
from utils.logs.debug_log import debug_enabled, debug_log, enable_debug
from utils.logs.pretty_log import pretty_log
from utils.visuals.pretty_defer import pretty_defer


class ChangeLogModal(discord.ui.Modal, title="Arceus Update Log"):
    log_content = discord.ui.TextInput(
        label="Update Log Content",
        style=discord.TextStyle.paragraph,
        placeholder="Enter the content for the Arceus update log message.",
        required=True,
        max_length=2000,
    )

    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    async def on_submit(self, interaction: discord.Interaction):
        debug_log(
            f"[ArceusUpdateLog] Modal submitted by user {interaction.user} (ID: {interaction.user.id})"
        )
        loader = await pretty_defer(
            interaction=interaction,
            content="Sending Arceus update log...",
            ephemeral=True,
        )
        if interaction.user.id not in [YUKI_USER_ID, KHY_USER_ID]:
            pretty_log(
                "info",
                f"Unauthorized user {interaction.user} (ID: {interaction.user.id}) attempted to submit Arceus update log.",
                label="Arceus Update Log",
            )
            await loader.error(
                content="Only Yuki and Khy are authorized to submit Arceus update logs.",
            )
            return


        log_message = self.log_content.value
        debug_log(f"[ArceusUpdateLog] Log message: {log_message}")
        pretty_log(
            "info",
            f"Received new Arceus update log content from {interaction.user} (ID: {interaction.user.id}): {log_message}",
            label="Arceus Update Log",
        )

        # Build the embed for the update log
        embed = discord.Embed(
            title=f"Changelog Update",
            description=log_message,
            color=ARCEUS_EMBED_COLOR,
        )

        # Send the embed to the change log channel
        change_log_channel = self.bot.get_channel(VN_ALLSTARS_TEXT_CHANNELS.change_log)
        if not change_log_channel:
            pretty_log(
                "error",
                f"Change log channel not found (ID: {VN_ALLSTARS_TEXT_CHANNELS.change_log})",
                label="Arceus Update Log",
            )
            await loader.error(
                content="Failed to send update log: Change log channel not found.",
            )
            return
        try:
            await send_webhook(
                channel=change_log_channel,
                content=None,
                embed=embed,
                bot=self.bot,
            )
            pretty_log(
                "info",
                f"Successfully sent Arceus update log to channel {change_log_channel.name} (ID: {change_log_channel.id})",
                label="Arceus Update Log",
            )
            await loader.success(
                content="Arceus update log sent successfully!",
            )
        except Exception as e:
            pretty_log(
                "error",
                f"Failed to send Arceus update log to channel {change_log_channel.name} (ID: {change_log_channel.id}): {e}",
                label="Arceus Update Log",
            )
            await loader.error(
                content="Failed to send update log. Please try again later.",
            )

class ArceusUpdateLog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="update-log",
        description="Send an update log message to the change log channel.",
    )
    async def arceus_update_log(self, interaction: discord.Interaction):
        try:
            modal = ChangeLogModal(self.bot)
            await interaction.response.send_modal(modal)

        except Exception as e:
            pretty_log(
                "error",
                f"Failed to send Arceus update log modal to {interaction.user} (ID: {interaction.user.id}): {e}",
                label="Arceus Update Log",
            )
            await interaction.response.send_message(
                content="An error occurred while trying to send the update log modal. Please try again later.",
                ephemeral=True,
            )

    arceus_update_log.extras = {"category": "Staff"}


async def setup(bot):
    await bot.add_cog(ArceusUpdateLog(bot))

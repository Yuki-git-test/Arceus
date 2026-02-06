import discord
from discord import app_commands
from discord.ext import commands

from Constants.aesthetic import Dividers
from Constants.clan_wars_constants import CLAN_WARS_SERVER_ID, CLAN_WARS_TEXT_CHANNELS
from Constants.vn_allstars_constants import ARCEUS_EMBED_COLOR
from utils.clan_wars.clan_wars_roles_embed import Clan_Wars_Roles_Button
from utils.clan_wars.general_roles_embed import General_Roles_Button
from utils.logs.pretty_log import pretty_log


class Main_Ping_Me_Roles_Embed_View(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        # Add Clan Wars Roles Button
        self.add_item(Clan_Wars_Roles_Button())
        # Add General Roles Button
        self.add_item(General_Roles_Button())


class Ping_Me_Roles(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # Register persistent views for reboot survival
        bot.add_view(Main_Ping_Me_Roles_Embed_View())

    @app_commands.command(
        name="ping-me-roles",
        description="Sends an embed with buttons to toggle your ping roles.",
    )
    # Only allow this command to be used by admins in the clan wars server
    @app_commands.checks.has_permissions(administrator=True)
    async def ping_me_roles(self, interaction: discord.Interaction):
        if interaction.guild_id != CLAN_WARS_SERVER_ID:
            await interaction.response.send_message(
                "This command can only be used in the Clan Wars server.", ephemeral=True
            )
            return

        guild = interaction.guild
        channel = guild.get_channel(CLAN_WARS_TEXT_CHANNELS.roles)
        if not channel:
            await interaction.response.send_message(
                "Roles channel not found. Please contact an administrator.",
                ephemeral=True,
            )
            return

        # Optional: delete previously sent ping me roles embeds by the bot
        async for msg in channel.history(limit=20):
            if msg.author.id == interaction.client.user.id and msg.components:
                try:
                    await msg.delete()
                    pretty_log(
                        "info",
                        "Deleted old Ping Me Roles embed message.",
                    )
                except:
                    pass
        title = "Clan Wars Roles"
        desc = "Role Categories:\n\n" "🏰 Clan Wars Roles\n" "⚜️ General Roles\n"
        embed = discord.Embed(title=title, description=desc, color=ARCEUS_EMBED_COLOR)
        embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
        embed.set_image(url=Dividers.clan_wars_ping_roles)
        try:
            await channel.send(embed=embed, view=Main_Ping_Me_Roles_Embed_View())
            await interaction.response.send_message(
                f"Sent the ping me roles embed in {channel.mention}", ephemeral=True
            )
        except Exception as e:
            pretty_log(
                "error",
                f"Failed to send Ping Me Roles embed in {channel.name}: {e}",
            )
            await interaction.response.send_message(
                "An error occurred while sending the embed. Please try again later.",
                ephemeral=True,
            )


async def setup(bot: commands.Bot):
    await bot.add_cog(Ping_Me_Roles(bot))

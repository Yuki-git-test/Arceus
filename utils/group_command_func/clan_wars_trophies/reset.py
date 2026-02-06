from datetime import datetime, timedelta

import discord
from discord import app_commands
from discord.ext import commands

from Constants.aesthetic import Thumbnails
from Constants.clan_wars_constants import CLAN_WARS_SERVER_ID, CLAN_WARS_TEXT_CHANNELS
from Constants.vn_allstars_constants import KHY_USER_ID
from utils.db.clan_wars_trophies_db import delete_all_clan_wars_trophies
from utils.functions.webhook_func import send_webhook
from utils.logs.pretty_log import pretty_log
from utils.visuals.pretty_defer import pretty_defer

TROPHY_THUMBNAIL_URL = Thumbnails.trophy


async def reset_trophies_func(
    bot: commands.Bot,
    interaction: discord.Interaction,
):
    guild = interaction.guild

    if interaction.guild_id != CLAN_WARS_SERVER_ID:
        await interaction.response.send_message(
            "This command can only be used in the Clan Wars server.", ephemeral=True
        )
        return

    # Defer response
    loader = await pretty_defer(
        interaction=interaction,
        content="Resetting all clan wars trophies...",
        ephemeral=False,
    )

    # Delete all trophies from the database
    await delete_all_clan_wars_trophies(bot)

    pretty_log(
        tag="info",
        message="All clan wars trophies have been reset.",
        label="Trophy Reset",
    )

    await loader.success(content="All clan wars trophies have been successfully reset.")
    embed = discord.Embed(
        title="🏆 Clan Wars Trophies Reset 🏆",
        description=f"All clan wars trophies have been reset by {interaction.user.mention}.",
        color=discord.Color.red(),
        timestamp=datetime.now(),
    )
    embed.set_thumbnail(url=TROPHY_THUMBNAIL_URL)
    embed.set_author(
        name=interaction.user.display_name,
        icon_url=interaction.user.display_avatar.url,
    )
    log_channel = guild.get_channel(CLAN_WARS_TEXT_CHANNELS.server_logs)
    if log_channel:
        await send_webhook(
            bot,
            log_channel,
            embed=embed,
        )

from datetime import datetime, timedelta

import discord
from discord import app_commands
from discord.ext import commands

from Constants.aesthetic import Thumbnails
from Constants.clan_wars_constants import CLAN_WARS_SERVER_ID, CLAN_WARS_TEXT_CHANNELS
from Constants.vn_allstars_constants import KHY_USER_ID
from utils.db.clan_wars_trophies_db import (
    fetch_all_clan_wars_trophies,
    fetch_clan_wars_trophy,
    fetch_current_leaderboard_info,
    upsert_clan_wars_trophy,
    upsert_leaderboard_msg_id,
)
from utils.functions.webhook_func import send_webhook
from utils.logs.pretty_log import pretty_log
from utils.visuals.pretty_defer import pretty_defer

TROPHY_THUMBNAIL_URL = Thumbnails.trophy
from .update_leaderboard import create_leaderboard_embed


# 🍭──────────────────────────────
#   🎀 View Leaderboard Command Function
# 🍭──────────────────────────────
async def view_leaderboard_func(
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
        content="Fetching leaderboard...",
        ephemeral=False,
    )

    embed = await create_leaderboard_embed(bot, guild)

    await loader.success(embed=embed, content="")

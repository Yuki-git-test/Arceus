from datetime import datetime, timedelta

import discord
from discord import app_commands
from discord.ext import commands

from Constants.aesthetic import Thumbnails
from Constants.clan_wars_constants import CLAN_WARS_TEXT_CHANNELS
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


def format_trophy_amount(amount: int) -> str:
    """Formats the trophy amount with commas."""
    return f"🏆 **{amount:,}**"


async def create_leaderboard_embed(
    bot: commands.Bot,
    guild: discord.Guild,
):
    """Creates a clan wars trophies leaderboard embed."""

    embed = discord.Embed(
        title="🏆 Clan Wars Trophies Leaderboard 🏆",
        color=discord.Color.gold(),
    )
    trophies_dict = await fetch_all_clan_wars_trophies(bot)
    if not trophies_dict:
        embed.description = "No clan wars trophies data available."
        return embed
    # Convert dict to list of dicts for sorting
    all_trophies = [
        {"role_id": role_id, "clan_name": data["clan_name"], "amount": data["amount"]}
        for role_id, data in trophies_dict.items()
    ]
    # Sort trophies by amount in descending order
    sorted_trophies = sorted(all_trophies, key=lambda x: x["amount"], reverse=True)
    pretty_log(
        tag="info",
        message="Creating trophy leaderboard embed with trophies data.",
        label="Trophy Leaderboard Embed",
    )
    for index, trophy_info in enumerate(sorted_trophies[:25], start=1):
        role_id = trophy_info["role_id"]
        clan_name = trophy_info["clan_name"]
        amount = trophy_info["amount"]
        amount = format_trophy_amount(amount)
        role = guild.get_role(role_id)
        if role:
            embed.add_field(
                name=f"{index}. {clan_name}",
                value=f"> - {amount}",
                inline=False,
            )
    embed.set_thumbnail(url=TROPHY_THUMBNAIL_URL)
    embed.timestamp = datetime.now()
    embed.set_footer(text="Updated on", icon_url=guild.icon.url if guild.icon else None)
    return embed


async def update_leaderboard_func(
    bot: commands.Bot, guild: discord.Guild, user: discord.Member = None
):
    """Updates the clan wars trophies leaderboard in the designated channel."""
    leaderboard_channel = guild.get_channel(CLAN_WARS_TEXT_CHANNELS.point_leaderboard)
    if not leaderboard_channel:
        pretty_log(
            tag="error",
            message=f"Leaderboard channel with ID {CLAN_WARS_TEXT_CHANNELS.point_leaderboard} not found in guild '{guild.name}' (ID: {guild.id})",
        )
        return

    # Get message id
    current_leader_board_info = await fetch_current_leaderboard_info(bot)
    message_id = (
        current_leader_board_info["message_id"] if current_leader_board_info else None
    )
    if not message_id:
        pretty_log(
            tag="info",
            message="No existing leaderboard message ID found. Creating a new message.",
            label="Trophy Leaderboard Update",
        )
        leaderboard_embed = await create_leaderboard_embed(bot, guild)
        leaderboard_message = await leaderboard_channel.send(embed=leaderboard_embed)
        await upsert_leaderboard_msg_id(
            bot, leaderboard_message.id, leaderboard_channel
        )
        pretty_log(
            tag="success",
            message="Created new trophy leaderboard message.",
            label="Trophy Leaderboard Update",
        )
        return

    elif message_id:
        pretty_log(
            tag="info",
            message="Existing leaderboard message ID found. Updating the message.",
            label="Trophy Leaderboard Update",
        )
        try:
            leaderboard_message = await leaderboard_channel.fetch_message(message_id)
            leaderboard_embed = await create_leaderboard_embed(bot, guild)
            await leaderboard_message.edit(embed=leaderboard_embed)
            pretty_log(
                tag="success",
                message="Updated trophy leaderboard message.",
                label="Trophy Leaderboard Update",
            )
        except discord.NotFound:
            pretty_log(
                tag="error",
                message="Leaderboard message not found. Creating a new one.",
                label="Trophy Leaderboard Update",
            )
            leaderboard_embed = await create_leaderboard_embed(bot, guild)
            leaderboard_message = await leaderboard_channel.send(
                embed=leaderboard_embed
            )
            await upsert_leaderboard_msg_id(
                bot, leaderboard_message.id, leaderboard_channel
            )

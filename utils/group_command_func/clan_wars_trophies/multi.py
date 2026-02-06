import discord
from discord.ext import commands

from Constants.aesthetic import Thumbnails
from Constants.clan_wars_constants import CLAN_WARS_SERVER_ID, CLAN_WARS_TEXT_CHANNELS
from utils.db.clan_wars_trophies_db import (
    fetch_all_clan_wars_trophies,
    fetch_clan_wars_trophy,
    upsert_clan_wars_trophy,
)
from utils.functions.webhook_func import send_webhook
from utils.logs.pretty_log import pretty_log
from utils.visuals.pretty_defer import pretty_defer

TROPHY_THUMBNAIL_URL = Thumbnails.trophy

LOG_CHANNEL_ID = CLAN_WARS_TEXT_CHANNELS.server_logs
from datetime import datetime

from .update_leaderboard import format_trophy_amount, update_leaderboard_func


# 🍭──────────────────────────────
#   🎀 Trophies Multi Command Function
# 🍭──────────────────────────────
async def trophy_multi_func(
    bot: commands.Bot,
    interaction: discord.Interaction,
    action: str,
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
    guild = interaction.guild

    if interaction.guild_id != CLAN_WARS_SERVER_ID:
        await interaction.response.send_message(
            "This command can only be used in the Clan Wars server.", ephemeral=True
        )
        return

    # Defer response
    loader = await pretty_defer(
        interaction=interaction,
        content=f"{action.capitalize()}ing trophies...",
        ephemeral=False,
    )

    # Validate amount
    if amount <= 0:
        await loader.error("Invalid amount provided for trophies.")
        return

    # Get list of clans
    clans = [clan1, clan2, clan3, clan4, clan5, clan6, clan7, clan8, clan9, clan10]

    # Fetch all trophies for comparison
    """all_trophies = await fetch_all_clan_wars_trophies(bot)
    if not all_trophies:
        await loader.error("No clan wars trophies data available in the database.")
        return"""

    summary_lines = []
    # Process each clan
    for clan in clans:
        if clan is None:
            continue

        # Fetch current trophy count for the clan
        trophy_record = await fetch_clan_wars_trophy(bot, clan.id)
        current_amount = trophy_record["amount"] if trophy_record else 0
        current_amount_formatted = format_trophy_amount(current_amount)

        # Calculate new amount based on action
        if action == "add":
            new_amount = current_amount + amount
            new_amount_formatted = format_trophy_amount(new_amount)

            desc_line = (
                f"> - {clan.name}: {current_amount_formatted} ➔ {new_amount_formatted}"
            )
            summary_lines.append(desc_line)
        elif action == "remove":
            new_amount = max(current_amount - amount, 0)  # Prevent negative trophies
            desc_line = (
                f"> - {clan.name}: {current_amount_formatted} ➔ {new_amount_formatted}"
            )
            summary_lines.append(desc_line)
        else:
            await loader.error("Invalid action. Use 'add' or 'remove'.")
            return

        # Upsert the new trophy count in the database
        await upsert_clan_wars_trophy(bot, clan.id, clan.name, new_amount)
        pretty_log(
            "info",
            f"{action.capitalize()}ed {amount} trophies for '{clan.name}' (Role ID: {clan.id}). New total: {new_amount}",
            label="Trophy Update",
        )
    # Build confirmation embed
    action_str = "Added" if action == "add" else "Removed"
    title = f"🏆 {action_str} Trophies Summary"
    desc = f"**{amount} Amount {action_str.lower()} for each clan:**\n" + "\n".join(
        summary_lines
    )
    embed = discord.Embed(
        title=title,
        description=desc,
        color=discord.Color.gold(),
        timestamp=datetime.now(),
    )
    embed.set_thumbnail(url=TROPHY_THUMBNAIL_URL)
    embed.set_author(
        name=interaction.user.display_name,
        icon_url=interaction.user.display_avatar.url,
    )
    await loader.success(embed=embed, content="Trophies updated successfully!")

    # Log the update in the server logs channel
    log_channel = guild.get_channel(LOG_CHANNEL_ID)
    if log_channel:
        await send_webhook(bot, log_channel, embed=embed)

    # Update the leaderboard after processing all clans
    await update_leaderboard_func(bot, guild)

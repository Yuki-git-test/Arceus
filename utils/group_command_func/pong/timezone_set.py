import discord
import pytz
from discord import app_commands
from discord.ext import commands

from Constants.vn_allstars_constants import VN_ALLSTARS_TEXT_CHANNELS
from utils.db.timezone_db import set_user_timezone
from utils.functions.webhook_func import send_webhook
from utils.logs.pretty_log import pretty_log
from utils.visuals.design_embed import design_embed


# -------------------- [💙 AUTOCOMPLETE] --------------------
async def tz_autocomplete(
    interaction: discord.Interaction, current: str
) -> list[app_commands.Choice[str]]:
    matches = autocomplete_timezones(current)
    return [app_commands.Choice(name=tz, value=tz) for tz in matches]


# -------------------- [💙 VALIDATE] --------------------
def is_valid_timezone(tz: str) -> bool:
    """Check if a given string is a valid IANA timezone."""
    return tz in pytz.all_timezones


# -------------------- [💙 AUTOCOMPLETE LIST] --------------------
def autocomplete_timezones(current: str) -> list[str]:
    """Return a list of matching timezones for autocomplete."""
    current_lower = current.lower()
    matches = [tz for tz in pytz.all_timezones if current_lower in tz.lower()]
    return matches[:25]  # Discord limits autocomplete to 25 suggestions


async def reminder_set_timezone_func(
    bot: commands.Bot, interaction: discord.Interaction, timezone: str
):
    user = interaction.user
    user_id = user.id
    user_name = user.name

    # -------------------- [💙 SET TIMEZONE] --------------------
    await set_user_timezone(
        bot=bot, user_id=user_id, user_name=user_name, timezone=timezone
    )

    # -------------------- [💙 USER CONFIRM EMBED] --------------------
    user_embed = discord.Embed(
        title="Timezone set successfully", description=f"Timezone: {timezone}"
    )
    user_embed = design_embed(
        user=user,
        embed=user_embed,
    )

    # -------------------- [💙 SERVER LOG EMBED] --------------------
    server_embed = discord.Embed(
        title="Timezone updated",
        description=f"- Member: {user.mention}\n- Timezone: {timezone}",
    )
    server_embed = design_embed(
        user=user,
        embed=server_embed,
    )

    # -------------------- [💙 SEND EMBEDS] --------------------
    await interaction.response.send_message(embed=user_embed, ephemeral=True)

    # Server log
    log_channel = interaction.user.guild.get_channel(
        VN_ALLSTARS_TEXT_CHANNELS.member_logs
    )
    if log_channel:
        await send_webhook(
            bot=bot,
            channel=log_channel,
            embed=server_embed,
        )

    # -------------------- [💙 PRETTY LOG] --------------------
    pretty_log(
        "db",
        f"🌙 {user_name} ({user_id}) set timezone → {timezone}",
    )

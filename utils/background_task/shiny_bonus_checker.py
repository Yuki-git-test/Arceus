import time

import discord

from Constants.vn_allstars_constants import (
    VN_ALLSTARS_ROLES,
    VN_ALLSTARS_TEXT_CHANNELS,
    VNA_SERVER_ID,
)
from utils.db.shiny_bonus_db import delete_shiny_bonus, fetch_shiny_bonus
from utils.logs.pretty_log import pretty_log


async def check_and_handle_expired_shiny_bonus(bot):
    """Check if the shiny bonus has expired and handle its expiration."""
    shiny_bonus = await fetch_shiny_bonus(bot)
    if not shiny_bonus:
        return
    ends_on = shiny_bonus["ends_on"]
    current_time = int(time.time())
    if current_time >= ends_on:
        pretty_log(
            "info",
            "Shiny bonus has expired. Deleting bonus and notifying channels.",
        )
        await delete_shiny_bonus(bot)
        guild = bot.get_guild(VNA_SERVER_ID)
        # Notify all relevant channels
        channel = guild.get_channel(VN_ALLSTARS_TEXT_CHANNELS.bumps)
        role = guild.get_role(VN_ALLSTARS_ROLES.shiny_bonus)
        if channel and role:
            await channel.send(
                content=f"{role.mention} The Checklist Shiny Bonus has ended!",
            )

from datetime import datetime

import discord

from Constants.aesthetic import Thumbnails
from Constants.vn_allstars_constants import (
    ARCEUS_EMBED_COLOR,
    VN_ALLSTARS_ROLES,
    VN_ALLSTARS_TEXT_CHANNELS,
    VNA_SERVER_ID,
)
from utils.logs.pretty_log import pretty_log

holiday = False  # Set to False when not in holiday season


async def send_daily_ping(bot):
    guild = bot.get_guild(VNA_SERVER_ID)
    if not guild:
        pretty_log("warn", "Guild not found for daily ping.")
        return
    channel = guild.get_channel(VN_ALLSTARS_TEXT_CHANNELS.bumps)
    daily_role = guild.get_role(VN_ALLSTARS_ROLES.daily_ping)
    if not channel or not daily_role:
        pretty_log("warn", "Channel or role not found for daily ping.")
        return
    daily_checklist = (
        f"- ;daily - To claim your daily reward.\n"
        f"- ;hunt - To view your current hunt.\n"
        f"- ;sw - To claim your free 2x swap tickets\n"
    )
    holiday_add_on = (
        f"- ;ss join - To join the Secret Santa list,\n"
        f"- ;hiker - To help the hiker.\n"
        f"- ;xmas - To claim your free gifts in Pokemeow Official Server.\n"
    )
    desc = daily_checklist
    if holiday:
        desc += holiday_add_on

    embed = discord.Embed(
        title="Daily Checklist Reminder",
        description=desc,
        color=ARCEUS_EMBED_COLOR,
        timestamp=datetime.now(),
    )
    embed.set_thumbnail(url=Thumbnails.daily_ping)
    embed.set_footer(text=guild.name, icon_url=guild.icon.url if guild.icon else None)
    content = f"{daily_role.mention} Time to do your daily checklist!"
    await channel.send(content=content, embed=embed)
    pretty_log("info", "Sent daily ping message.")
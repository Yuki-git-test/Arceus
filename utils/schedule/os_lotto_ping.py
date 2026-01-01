# 🧧 loop_tasks/lotto_reminder.py with APScheduler & pretty logs

import zoneinfo
from datetime import datetime

import discord

from Constants.aesthetic import Thumbnails
from Constants.pokemon_gif import GOLDEN_POKEMON_URL
from Constants.vn_allstars_constants import (
    ARCEUS_EMBED_COLOR,
    VN_ALLSTARS_EMOJIS,
    VN_ALLSTARS_ROLES,
    VN_ALLSTARS_TEXT_CHANNELS,
    VNA_SERVER_ID,
)
from utils.essentials.cleanup_first_match import cleanup_first_match
from utils.logs.pretty_log import pretty_log

CHANNEL_ID = VN_ALLSTARS_TEXT_CHANNELS.bumps
OS_LOTTERY_ROLE_ID = VN_ALLSTARS_ROLES.os_lotto_ping

# Timezones
NYC = zoneinfo.ZoneInfo("America/New_York")

# 🎁 Lotto prize schedule: EST-based (0 = Monday, 6 = Sunday)
PRIZES = {
    6: {"name": "Slowpoke", "thumbnail": GOLDEN_POKEMON_URL.slowpoke},  # Sunday
    0: {"name": "Togedemaru", "thumbnail": GOLDEN_POKEMON_URL.togedemaru},  # Monday
    2: {"name": "Smeargle", "thumbnail": GOLDEN_POKEMON_URL.smeargle},  # Wednesday
    4: {
        "name": "Hisuian-Zorua",
        "thumbnail": GOLDEN_POKEMON_URL.hisuian_zorua,
    },  # Friday
}

OS_LOTTO_PHRASE = "OS LOTTO REMINDER"


# 🌇 Lotto Reminder Toggle View
class LottoReminderView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot
        self.message = None

    @discord.ui.button(
        label="Toggle OS Lotto Ping",
        style=discord.ButtonStyle.primary,
        custom_id="os_lotto_toggle_button",
    )
    async def toggle_lotto(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        role = interaction.guild.get_role(OS_LOTTERY_ROLE_ID)
        member = interaction.user

        if role in member.roles:
            await member.remove_roles(role, reason="Toggled OS Lotto Ping")
            await interaction.response.send_message(
                f"🎲 Removed {role.mention} role!", ephemeral=True
            )
        else:
            await member.add_roles(role, reason="Toggled OS Lotto Ping")
            await interaction.response.send_message(
                f"🎲 Added {role.mention} role!", ephemeral=True
            )


# 📩 Send Lotto Reminder
async def send_lotto_reminder(bot: discord.Client):
    now = datetime.now(tz=NYC)  # ⏰ Use EST/EDT for prize mapping
    weekday = now.weekday()
    prize_info = PRIZES.get(weekday)

    if not prize_info:
        return  # Not a lotto day

    guild = bot.get_guild(VNA_SERVER_ID)
    if not guild:
        pretty_log(
            tag="warn",
            message="Guild not found.",
            label="🎯 OS LOTTO",
        )
        return

    channel = guild.get_channel(CHANNEL_ID)
    if not channel:
        pretty_log(
            tag="warn",
            message="Channel not found.",
            label="🎯 OS LOTTO",
        )
        return
    # Cleans up previously view
    await cleanup_first_match(
        bot=bot, channel=channel, phrase=OS_LOTTO_PHRASE, component="description"
    )

    content = f"<@&{OS_LOTTERY_ROLE_ID}> 10 Minutes before lottery ends!"

    embed = discord.Embed(
        description=(
            f"### 🎯 **OS LOTTO REMINDER**\n"
            f"- **1st Prize:** {VN_ALLSTARS_EMOJIS.vna_golden} **{prize_info['name']}**\n"
            f"- **Command:** `;lot buy <amount>`"
        ),
        color=ARCEUS_EMBED_COLOR,
    )
    embed.set_thumbnail(url=prize_info["thumbnail"])
    view = LottoReminderView(bot)
    msg = await channel.send(content=content, embed=embed, view=view)
    view.message = msg

    pretty_log(
        tag="info",
        message=f"Sent reminder for {prize_info['name']} ({now.strftime('%A EST')}).",
        label="🎯 OS LOTTO",
    )

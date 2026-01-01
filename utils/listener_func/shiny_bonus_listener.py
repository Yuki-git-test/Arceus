import re
from datetime import datetime

import discord
from discord.ext import commands

from Constants.aesthetic import Emojis, Thumbnails
from Constants.vn_allstars_constants import (
    VN_ALLSTARS_EMOJIS,
    VN_ALLSTARS_ROLES,
    VN_ALLSTARS_TEXT_CHANNELS,
    VNA_SERVER_ID
)
from utils.db.shiny_bonus_db import (
    extend_shiny_bonus,
    fetch_shiny_bonus,
    update_shiny_bonus_ends_on,
    update_shiny_bonus_message_id,
    upsert_shiny_bonus,
)
from utils.essentials.cleanup_first_match import cleanup_first_match
from utils.logs.debug_log import debug_log, enable_debug
from utils.logs.pretty_log import pretty_log

BONUS_NAME = f"{Emojis.shiny_bo} Checklist Shiny Bonus Active!"
BONUS_EFFECT = f"+25% {VN_ALLSTARS_EMOJIS.vna_shiny} Checklist Pokemon spawn rates."
NEW_EMOJI = "🆕"
PLUS_EMOJI = "➕"


class ToggleShinyBonusButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Toggle Shiny Bonus Ping",
        emoji=VN_ALLSTARS_EMOJIS.vna_shiny,
        style=discord.ButtonStyle.secondary,
        custom_id="toggle_shiny_bonus_button",
    )
    async def toggle_shiny_bonus(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        shiny_bonus_role = interaction.guild.get_role(VN_ALLSTARS_ROLES.shiny_bonus)
        if not shiny_bonus_role:
            await interaction.response.send_message(
                "Shiny Bonus role not found in this server.", ephemeral=True
            )
            return
        member = interaction.user
        if shiny_bonus_role in member.roles:
            await member.remove_roles(shiny_bonus_role)
            await interaction.response.send_message(
                f"Removed {shiny_bonus_role.mention} from you.", ephemeral=True
            )
        else:
            await member.add_roles(shiny_bonus_role)
            await interaction.response.send_message(
                f"Added {shiny_bonus_role.mention} to you.", ephemeral=True
            )


# 🌸────────────────────────────────────────────
#     📦 Embed: New Shiny Bonus Announcement
# 🌸────────────────────────────────────────────
async def build_new_shiny_bonus_embed(
    bot: discord.Client,
    channel: discord.TextChannel,
    ends_on: int,
) -> discord.Embed:

    await cleanup_first_match(
        bot=bot, channel=channel, phrase=BONUS_NAME, component="title"
    )
    embed = discord.Embed(
        title=BONUS_NAME,
        description=(
            f"• Bonus effect: {BONUS_EFFECT}\n"
            f"• {NEW_EMOJI} The bonus ends <t:{ends_on}:R>"
        ),
        color=0xFADADD,  # 🩰 Soft pastel pink
    )

    return embed


# 🌼────────────────────────────────────────────
#   🔁 Embed: Shiny Bonus Extended Announcement
# 🌼────────────────────────────────────────────
async def build_extended_shiny_bonus_embed(
    bot: commands.Bot,
    channel: discord.TextChannel,
    ends_on: int,
    added_duration_str: str,
) -> discord.Embed:

    await cleanup_first_match(
        bot=bot, channel=channel, phrase=BONUS_NAME, component="title"
    )
    embed = discord.Embed(
        title=BONUS_NAME,
        description=(
            f"• Bonus effect: {BONUS_EFFECT}\n"
            f"• {PLUS_EMOJI} The bonus (+{added_duration_str}) now ends <t:{ends_on}:R>"
        ),
        color=0xFADADD,
    )

    return embed


async def handle_pokemeow_global_bonus(
    bot: commands.Bot, message: discord.Message, delta_seconds: int = 0
) -> bool:
    """💎 Check PokéMeow embed and post/update shiny bonus in multiple servers."""
    if not message.embeds:
        return False

    embed = message.embeds[0]
    desc = embed.description or ""

    # 🔍 Extract expiration timestamp
    match = re.search(
        r"- <:\w+:\d+> \+25% Checklist Shiny rate: <:\w+:\d+> Active, expires <t:(\d+):R>",
        desc,
    )
    if not match:
        return False

    expires_unix = int(match.group(1))
    # Return if expiration is less than an hour away
    if expires_unix - int(datetime.now().timestamp()) < 3600:
        return False

    expires_dt = datetime.fromtimestamp(expires_unix)

    guild = bot.get_guild(VNA_SERVER_ID)

    channel = guild.get_channel(VN_ALLSTARS_TEXT_CHANNELS.bumps)
    role = guild.get_role(VN_ALLSTARS_ROLES.shiny_bonus)
    if not channel or not role:
        pretty_log(
            "warn",
            f"channel or role not found, skipping.",
        )

    # 🗄 DB: fetch active bonus for this guild
    active_bonus = await fetch_shiny_bonus(bot=bot)

    if active_bonus:
        old_msg_id = active_bonus["message_id"]
        old_ends_unix = active_bonus["ends_on"]

        # ✅ Only extend if expiration has changed
        if old_ends_unix == expires_unix:
            pretty_log(
                "info",
                f"Bonus already up-to-date, skipping.",
            )

        # Determine seconds to add
        added_seconds = delta_seconds or max(0, expires_unix - old_ends_unix)
        if added_seconds <= 0:
            pretty_log(
                "info",
                f"no additional seconds to extend, skipping.",
            )
            return

        new_ends_unix = old_ends_unix + added_seconds
        new_ends_dt = datetime.fromtimestamp(new_ends_unix)

        # Human-readable duration
        if added_seconds < 60:
            added_str = f"{added_seconds} seconds"
        elif added_seconds < 3600:
            added_str = f"{added_seconds // 60} minutes"
        elif added_seconds < 86400:
            added_str = f"{added_seconds // 3600} hours"
        else:
            added_str = f"{added_seconds // 86400} days"

        # Build extended embed
        new_embed = await build_extended_shiny_bonus_embed(
            bot=bot,
            channel=channel,
            ends_on=new_ends_dt,
            added_duration_str=added_str,
        )

        # Delete old message
        try:
            old_msg = await channel.fetch_message(old_msg_id)
            await old_msg.delete()
        except discord.NotFound:
            pretty_log(
                "warn",
                f"Old shiny bonus message not found for deletion.",
            )

        # Send updated message
        new_msg = await channel.send(
            content=f"{role.mention} has been extended (+{added_str})",
            embed=new_embed,
            view=ToggleShinyBonusButton(),
        )

        # Update DB
        await update_shiny_bonus_message_id(
            bot=bot,
            message_id=new_msg.id,
        )
        await extend_shiny_bonus(bot=bot, seconds=added_seconds)

        pretty_log(
            "info" f"Extended bonus, new message {new_msg.id}",
        )

    else:
        # 🌟 No active bonus, create one
        new_msg = await channel.send(
            content=f"{role.mention} Activated!",
            embed=await build_new_shiny_bonus_embed(
                bot=bot, channel=channel, ends_on=expires_unix
            ),
            view=ToggleShinyBonusButton(),
        )
        started_on = int(datetime.now().timestamp())
        await upsert_shiny_bonus(
            bot=bot,
            message_id=new_msg.id,
            started_on=started_on,
            ends_on=expires_unix,
        )

        pretty_log(
            "info",
            f"Created new bonus, message {new_msg.id}",
        )

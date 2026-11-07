import re
from datetime import datetime

import discord

from Constants.vn_allstars_constants import (
    DEFAULT_EMBED_COLOR,
)
from utils.functions.webhook_func import send_webhook
from utils.logs.pretty_log import pretty_log
from utils.listener_func.res_egg_listener import get_rarespawn_channel

def extract_set_emoji_url(text: str) -> str | None:
    """
    Extracts the custom Discord emoji that appears after the word 'Set' and returns its CDN image URL.
    """
    match = re.search(r"Set\s+(<a?:[a-zA-Z0-9_]+:\d+>)", text)
    if match:
        emoji = match.group(1)
        emoji_match = re.match(r"<(a?):([a-zA-Z0-9_]+):(\d+)>", emoji)
        if emoji_match:
            is_animated = emoji_match.group(1) == "a"
            emoji_id = emoji_match.group(3)
            ext = "gif" if is_animated else "png"
            return f"https://cdn.discordapp.com/emojis/{emoji_id}.{ext}"
    return None


async def icon_unlock_listener(bot: discord.Client, message: discord.Message):
    embed = message.embeds[0] if message.embeds else None
    if not embed:
        return

    embed_description = embed.description or ""

    # Extract the user who unlocked the icon from the embed description
    user_match = re.search(r"<@!?(\d+)>", embed_description)
    if not user_match:
        return

    user_id = int(user_match.group(1))
    guild = message.guild
    member = guild.get_member(user_id) or await guild.fetch_member(user_id)
    if not member:
        return

    battle_unlock_channel = get_rarespawn_channel(guild)
    if not battle_unlock_channel:
        pretty_log(
            "error",
            f"Battle Unlocks channel not found in guild '{guild.name}' (ID: {guild.id})",
        )

    # Extract icon name
    match = re.search(r"/battle set-icon\s+([^\s`]+)", embed_description)
    if not match:
        pretty_log(
            tag="info",
            message=f"Skipped: No icon name found in message {message.id}",
            label="Icon Extract",
        )
        return

    icon_name = match.group(1)
    pretty_log(
        tag="info",
        message=f"Found icon name '{icon_name}' in message {message.id} in channel '{message.channel.name}'",
        label="Icon Extract",
    )

    display_icon_name = icon_name.replace("_", " ").title()
    thumbnail_url = extract_set_emoji_url(embed_description)
    if thumbnail_url:
        pretty_log(
            tag="info",
            message=f"Thumbnail URL for icon '{icon_name}' extracted from emoji in message {message.id} in channel '{message.channel.name}",
            label="Icon Asset",
        )
    else:
        thumbnail_url = member.display_avatar.url

    author_text = f"{member.display_name}"
    desc = f"**Icon Name:** {display_icon_name}"

    footer_text = f"Icon unlocked in {guild.name}"
    embed = discord.Embed(
        title="Icon Unlocked! 🛡️",
        url=message.jump_url,
        description=desc,
        color=DEFAULT_EMBED_COLOR,
        timestamp=datetime.now(),
    )
    embed.set_author(name=author_text, icon_url=member.display_avatar.url)
    embed.set_thumbnail(url=thumbnail_url)
    embed.set_footer(text=footer_text, icon_url=guild.icon.url if guild.icon else None)

    if battle_unlock_channel:
        await send_webhook(bot=bot, channel=battle_unlock_channel, embed=embed)

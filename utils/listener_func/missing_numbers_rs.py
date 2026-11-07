import re
from urllib.parse import urlparse

import discord

from Constants.vn_allstars_constants import (
    DEFAULT_EMBED_COLOR,
)
from utils.functions.webhook_func import send_webhook
from utils.logs.pretty_log import pretty_log

from utils.listener_func.res_egg_listener import get_rarespawn_channel

def is_valid_url(url: str) -> bool:
    try:
        result = urlparse(url)
        return all([result.scheme in ("http", "https"), result.netloc])
    except Exception:
        return False


def extract_info(text: str | None):
    if not text:
        return None, None

    # Strip custom emoji tokens (e.g. <:name:id> or <a:name:id>) and markdown escapes
    # so the surrounding punctuation doesn't break the bold-name/bold-prize matching.
    cleaned = re.sub(r"<a?:\w+:\d+>", "", text)
    cleaned = re.sub(r"\\(?=[._*~`|>])", "", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()

    bold_matches = re.findall(r"\*\*(.+?)\*\*", cleaned, flags=re.DOTALL)

    member_name = bold_matches[0].strip() if bold_matches else None
    missing_number = bold_matches[-1].strip() if len(bold_matches) >= 2 else None

    pretty_log(
        "info",
        f"Extracted member_name='{member_name}' and missing_number='{missing_number}' from text: {text}",
    )

    return member_name, missing_number


# 🎉────────────────────────────────────────────
#   💠 Pokémon Code Claim Handler (Patched)
# 🎉────────────────────────────────────────────
async def send_missing_number_claim_to_rs(
    bot: discord.Client, message: discord.Message
) -> str | None:
    """
    Extracts the member name and missing number from a missing number claim message and posts an embed in the rare spawn tracker channel.
    Handles shiny/golden properly and applies correct embed color.
    """

    embed = message.embeds[0] if message.embeds else None
    if not embed:
        return

    embed_description = embed.description if embed else ""
    embed_image_url = embed.image.url if embed and embed.image else None
    embed_color = embed.color if embed else DEFAULT_EMBED_COLOR

    try:
        member_name, prize = extract_info(embed_description)
        # Find member object in guild via user_name or display_name (case-insensitive fallback)
        guild = message.guild
        member = discord.utils.find(
            lambda m: m.name.lower() == (member_name or "").lower()
            or m.display_name.lower() == (member_name or "").lower(),
            guild.members,
        )

        achievement_channel = get_rarespawn_channel(guild)
        if not achievement_channel:
            pretty_log(
                "critical",
                f"Acheievements channel not found in guild {guild.name} ({guild.id})",
            )
            return

        if not member:
            pretty_log(
                "warning",
                f"Could not resolve member '{member_name}' in guild {guild.name} ({guild.id}); falling back to plain name",
            )

        member_display = member.mention if member else (member_name or "Someone")

        # ──────────────────────────────────────────────
        #   ✅ Build & send embed
        # ──────────────────────────────────────────────
        embed = discord.Embed(
            title="Missing Number Quest Completed",
            url=message.jump_url,
            description=f"{member_display} has received **{prize}**!",
            color=embed_color,
        )
        if embed_image_url:
            embed.set_image(url=embed_image_url)
        embed.set_author(
            name=member_name,
            icon_url=member.avatar.url if member and member.avatar else None,
        )

        await send_webhook(
            bot=bot,
            channel=achievement_channel,
            embed=embed,
        )

        pretty_log(
            "ready",
            f"Successfully posted Pokémon code claim for {member_name} (Message ID {message.id})",
        )

    except Exception as e:
        pretty_log(
            "critical",
            f"Unexpected error in send_missing_number_claim_to_rs (Message ID {getattr(message, 'id', 'unknown')}): {e}",
        )

import re
from datetime import datetime
from urllib.parse import urlparse

import discord

from Constants.aesthetic import Emojis
from Constants.paldea_galar_dict import rarity_meta
from utils.visuals.get_pokemon_gif import get_pokemon_gif
from utils.pokemeow.get_pokemeow_reply import get_pokemeow_reply_or_interaction_member
from utils.functions.pokemon_func import get_dex_number_by_name, get_mon_value
from utils.functions.webhook_func import send_webhook
from utils.logs.debug_log import debug_log
from utils.logs.pretty_log import pretty_log
from utils.listener_func.res_egg_listener import get_rarespawn_channel

def is_valid_url(url: str) -> bool:
    try:
        result = urlparse(url)
        return all([result.scheme in ("http", "https"), result.netloc])
    except Exception:
        return False


def extract_prize(text):
    """
    Extracts the prize name (e.g., 'Shiny Quaxly') from a message like:
    'You claimed a code for a <:Shiny:667126233217105931> <:912:1194246013934911488> Shiny Quaxly!'
    Returns the string between the last emoji and the exclamation mark.
    """
    match = re.search(r"(?:<:[^>]+> )+([^\!]+)!", text)
    if match:
        return match.group(1).strip()
    return None


# 🎉────────────────────────────────────────────
#   💠 Pokémon Code Claim Handler (Patched)
# 🎉────────────────────────────────────────────
async def send_code_claim_to_rs(
    bot: discord.Client, message: discord.Message
) -> str | None:
    """
    Extracts the Pokémon name from a code claim message and posts an embed in the rare spawn tracker channel.
    Handles shiny/golden properly and applies correct embed color.
    """
    try:
        member = await get_pokemeow_reply_or_interaction_member(message=message)
        if not member:
            pretty_log(
                "info",
                f"Skipping code-claim rare-spawn post: could not resolve member for message ID {message.id}",
            )
            return
        guild = member.guild

        achievement_channel = get_rarespawn_channel(guild)
        if not achievement_channel:
            pretty_log(
                "critical",
                f"Acheievements channel not found in guild {guild.name} ({guild.id})",
            )
            return

        content = (
            message.content if isinstance(message, discord.Message) else str(message)
        )
        # Primary: bold text e.g. "**Shiny Miraidon**" (prefix command response)
        # Fallback: text after emojis before "!" e.g. "🎁 🦎 Shiny Miraidon!" (slash command response)
        raw_pokemon_name = re.search(r"\*\*(.*?)\*\*", content) or re.search(
            r"(?:(?:<:[^>]+>|[^\w\s]) )+([A-Za-z][\w\s]*?)!", content
        )
        if not raw_pokemon_name:
            pretty_log(
                "critical",
                f"Failed to extract Pokémon name from message ID {message.id}",
            )
            return

        clean_pokemon_name = raw_pokemon_name.group(1).strip()
        pokemon_name_lower = clean_pokemon_name.lower()

        # ──────────────────────────────────────────────
        #   ✅ Rarity Detection (before replacements)
        # ──────────────────────────────────────────────
        rarity_key = "default"
        if "golden" in pokemon_name_lower:
            rarity_key = "golden"
        elif "shiny" in pokemon_name_lower:
            rarity_key = "shiny"

        rarity_info = rarity_meta.get(rarity_key, rarity_meta["unknown"])
        color = rarity_info["color"]
        display_name = clean_pokemon_name
        dex_number = get_dex_number_by_name(clean_pokemon_name)
        dex_suffix = f" #{dex_number}" if dex_number is not None else ""

        # ──────────────────────────────────────────────
        #   ✅ Replace keyword with emoji (case-insensitive)
        # ──────────────────────────────────────────────
        if rarity_key in ("golden", "shiny"):
            display_name = re.sub(
                rarity_key,
                rarity_info["emoji"],
                display_name,
                flags=re.IGNORECASE,
            ).strip()

        # ──────────────────────────────────────────────
        #   ✅ Build & send embed
        # ──────────────────────────────────────────────
        footer_text = f"Claimed in {message.guild.name}"
        embed = discord.Embed(
            title="Code Claimed",
            url=message.jump_url,
            description=f"{member.mention} has claimed a code for **{display_name}{dex_suffix}**!\n\u200b",
            color=color,
            timestamp=datetime.now(),
        )
        embed.set_author(name=member.display_name, icon_url=member.display_avatar.url)
        pokemon_gif = get_pokemon_gif(pokemon_name_lower)
        if pokemon_gif:
            embed.set_image(url=pokemon_gif)
        embed.set_footer(
            text=footer_text,
            icon_url=(
                message.guild.icon.url if message.guild and message.guild.icon else None
            ),
        )

        mon_value = await get_mon_value(bot, pokemon_name_lower)
        if mon_value and mon_value.get("has_market_value"):
            last_seen = mon_value.get("last_seen")
            last_seen_text = (
                f"Value as of {last_seen}" if last_seen != "N/A" else "Value"
            )
            current_listing = mon_value.get("current_listing")
            embed.add_field(name=last_seen_text, value=current_listing, inline=False)
            debug_log(f"Added market value to announcement: {current_listing!r}.")
        else:
            debug_log(f"No market value available for {pokemon_name_lower}.")
        await send_webhook(
            bot=bot,
            channel=achievement_channel,
            embed=embed,
        )

        pretty_log(
            "ready",
            f"Successfully posted Pokémon code claim for {display_name} (Message ID {message.id})",
        )

    except Exception as e:
        pretty_log(
            "critical",
            f"Unexpected error in send_code_claim_to_rs (Message ID {getattr(message, 'id', 'unknown')}): {e}",
        )

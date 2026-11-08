import re
from datetime import datetime
from urllib.parse import urlsplit, urlunsplit

import discord

from Constants.aesthetic import *
from Constants.vn_allstars_constants import DEFAULT_EMBED_COLOR
from Constants.wb_constants import *
from utils.visuals.get_pokemon_gif import get_pokemon_gif
from utils.functions.webhook_func import send_webhook
from utils.logs.debug_log import debug_log, enable_debug
from utils.logs.pretty_log import pretty_log
from utils.listener_func.res_egg_listener import get_rarespawn_channel
from utils.functions.pokemon_func import get_dex_number_by_name, get_mon_value

# 🎯 Define your criteria
SPECIAL_POKEMON_KEYWORDS = {"Shiny", "Gigantamax"}  # keywords to look for


SPECIAL_ITEMS = {
    "Ability Shield": Emojis.Ability_Shield,
    "Big Root": Emojis.Big_root,
    "Choice cloak": Emojis.Choice_Cloak,
    "Wise glasses": Emojis.Wise_Glasses,
    "Metronome": Emojis.Metronome,
    "Loaded dice": Emojis.Loaded_Dice,
}

# 🧠 Dedupe: reward message IDs already processed (on_message + on_message_edit)
_PROCESSED_WB_REWARD_IDS: set[int] = set()


def get_stable_embed_image_url(image_url: str) -> str:
    """Remove expiring query parameters from Discord attachment URLs."""
    if not image_url:
        return image_url

    parsed_url = urlsplit(image_url)
    if parsed_url.hostname not in {"media.discordapp.net", "cdn.discordapp.com"}:
        return image_url
    if not parsed_url.path.startswith("/attachments/"):
        return image_url

    return urlunsplit(
        (
            "https",
            "cdn.discordapp.com",
            parsed_url.path,
            "",
            "",
        )
    )


def get_gmax_assets(name: str, shiny: bool = False) -> dict[str, str | int] | None:
    """
    Fetch URLs, emoji, and embed color for a given Gmax/Eternamax Pokémon.

    Parameters
    ----------
    name : str
        The Pokémon name (lowercase, e.g., "charizard", "eternatus").
    shiny : bool, optional
        Whether to fetch the shiny assets. Default False.

    Returns
    -------
    dict or None
        Dictionary containing:
            - "sprite": gif URL of the Pokémon
            - "emoji": emoji URL for the Pokémon
            - "color": embed color (int)
        Returns None if not found.
    """
    # Pick the right URL + emoji class
    url_class = SHINY_GMAX_URL if shiny else REGULAR_GMAX_URL
    emoji_class = SHINY_GMAX_EMOJI if shiny else REG_GMAX_EMOJI

    # Get sprite, emoji, and color
    sprite = getattr(url_class, name, None)
    emoji = getattr(emoji_class, name, None)
    color = getattr(WBColors, name, None)

    if not sprite or not emoji or not color:
        return None

    return {
        "sprite": sprite,
        "emoji": emoji,
        "color": color,
    }


# ─────────────────────────────
# 🔹 Helper: Extract base species from a Pokémon name
# ─────────────────────────────
def extract_species_key(poke_name: str) -> str:
    """Return the base species key for sprite lookup, handling special cases, Gmax, Eternamax, and hyphens."""
    poke_name_lower = poke_name.lower().strip()

    if "golden onix" in poke_name_lower:
        return "golden_onix"

    if "eternatus" in poke_name_lower:
        return "eternatus"

    if "urshifu" in poke_name_lower:
        if "rapidstrike" in poke_name_lower:
            return "urs"
        if "singlestrike" in poke_name_lower:
            return "uss"

    cleaned = poke_name_lower.replace("shiny", "").strip()

    if "gigantamax" in cleaned:
        cleaned = cleaned.replace("gigantamax-", "").replace("gigantamax", "").strip()

    cleaned = re.sub(r"[\s\-]+", "_", cleaned)
    return cleaned


# ─────────────────────────────
# 🔹 Helper: Get thumbnail URL for Pokémon
# ─────────────────────────────
def get_pokemon_thumbnail(poke_name: str):
    poke_name_lower = poke_name.lower().strip()
    species_key = extract_species_key(poke_name)

    if "golden onix" in poke_name_lower:
        return GOLDEN_ONIX_URL

    if "eternatus" in poke_name_lower:
        if "shiny" in poke_name_lower:
            return getattr(SHINY_GMAX_URL, species_key, None)
        return getattr(REGULAR_GMAX_URL, species_key, None)

    if "shiny" in poke_name_lower and "gigantamax" in poke_name_lower:
        return getattr(SHINY_GMAX_URL, species_key, None)

    if "gigantamax" in poke_name_lower:
        return getattr(REGULAR_GMAX_URL, species_key, None)

    if "shiny" in poke_name_lower:
        return f"https://play.pokemonshowdown.com/sprites/ani-shiny/{species_key}.gif?quality=lossless"

    return f"https://play.pokemonshowdown.com/sprites/ani/{species_key}.gif?quality=lossless"


# ─────────────────────────────
# 🔹 Main reward handler (patched)
# ─────────────────────────────
async def handle_wb_rewards(
    bot: discord.Client, message: discord.Message, test_member: discord.Member = None
):
    try:
        debug_log("Entered handle_wb_rewards()", highlight=True)

        # 🛑 Skip if this rewards message was already handled (create/edit dedupe)
        if message.id in _PROCESSED_WB_REWARD_IDS:
            debug_log(f"Skipping already-processed WB rewards message {message.id}")
            return

        # 🛑 Only process PokéMeow bot messages
        author_str = str(message.author).lower()
        if "pokémeow" not in author_str and "pokemeow" not in author_str:
            return
        if not getattr(message, "embeds", None):
            return

        embed = message.embeds[0]
        description = embed.description or ""

        # ──────────────
        # Ensure it's a WB reward embed
        # ──────────────
        title = embed.title or ""
        if not ("Here are your rewards" in title and "(Boss id:" in title):
            return

        found_items = []
        found_pokemon = []

        # Extract special items
        for line in description.splitlines():
            for item_name, item_emoji in SPECIAL_ITEMS.items():
                if item_name.lower() in line.lower():
                    found_items.append((item_emoji, item_name))

        # Extract Pokémon
        for line in description.splitlines():
            if "Pokémon received" in line or "Pokemon received" in line:
                continue
            if line.strip().startswith("-") or line.strip().startswith("✨"):
                poke_name = line.lstrip(" -•\t✨").strip()
                poke_name_clean = re.sub(r"[*_~`]", "", poke_name)
                poke_name_clean = re.sub(r"<:[^:]+:\d+>", "", poke_name_clean)
                poke_name_clean = re.sub(r"\s*:[^:\s]+:\s*$", "", poke_name_clean)
                poke_name_clean = re.sub(
                    r"^(You obtained a|You obtained an|You received a)\s+",
                    "",
                    poke_name_clean,
                    flags=re.IGNORECASE,
                ).strip()
                poke_name_clean = re.sub(r"\W+$", "", poke_name_clean).strip()

                # ✅ Only keep if starts with desired prefixes (case-insensitive)
                valid_prefixes = [
                    "shiny gigantamax",
                    "gigantamax",
                    "golden",
                    "shiny eternamax",
                    "eternamax",
                    "shiny",
                ]
                if not any(
                    poke_name_clean.lower().startswith(prefix)
                    for prefix in valid_prefixes
                ):
                    continue

                if poke_name_clean.lower() in (
                    name.lower() for name in SPECIAL_ITEMS.keys()
                ):
                    continue
                if poke_name_clean and poke_name_clean not in found_pokemon:
                    found_pokemon.append(poke_name_clean)

        # ──────────────
        # Bail early if nothing special found
        # ──────────────
        if not found_items and not found_pokemon:
            debug_log("No special items or Pokémon found in rewards embed, skipping.")
            return  # nothing worth logging

        # ──────────────
        # Determine member
        # ──────────────
        if test_member:
            member = test_member
        else:
            user_msg = getattr(message, "reference", None) and getattr(
                message.reference, "resolved", None
            )
            member = user_msg.author if isinstance(user_msg, discord.Message) else None

            # 🔄 Fallback: fetch the replied-to message if it wasn't resolved
            #    (resolved is None when Discord omits referenced_message and the
            #    original message fell out of the bot's message cache)
            if (
                not member
                and message.reference
                and getattr(message.reference, "message_id", None)
            ):
                try:
                    ref_msg = await message.channel.fetch_message(
                        message.reference.message_id
                    )
                    member = ref_msg.author
                except Exception as e:
                    pretty_log(
                        "warning",
                        f"WB rewards: failed to fetch replied-to message {message.reference.message_id}: {e}",
                        label="🎁 PokéMeow",
                    )

        # 🛑 Require a valid member (PokéMeow must be replying to someone)
        if not member:
            pretty_log(
                "warning",
                f"WB rewards skipped for message ID {message.id}: could not resolve the replied-to member.",
                label="🎁 PokéMeow",
            )
            return

        # ──────────────
        # Build embed
        # ──────────────
        challenge_name = re.sub(
            r"🎁 Here are your rewards for (the )?",
            "",
            embed.title or "",
            flags=re.IGNORECASE,
        ).strip()

        # Remove any custom emoji codes like <:emoji_name:123456>
        challenge_name = re.sub(r"<:[^:]+:\d+>", "", challenge_name).strip()

        embed_color = DEFAULT_EMBED_COLOR
        display_pokemon = []

        if found_pokemon:
            poke_name = found_pokemon[0]
            poke_lower = poke_name.lower()

            is_shiny = "shiny" in poke_lower
            rarity_emoji = None
            if "golden" in poke_lower:
                rarity_emoji = RARITY_DICT["golden"]["emoji"]
                embed_color = RARITY_DICT["golden"]["color"]
            elif is_shiny:
                rarity_emoji = RARITY_DICT["shiny"]["emoji"]
                embed_color = RARITY_DICT["shiny"]["color"]

            if "gigantamax" in poke_lower or "eternatus" in poke_lower:
                species_key = extract_species_key(poke_name)
                gmax_data = GMAX_DICT.get(species_key)
                if gmax_data:
                    sprite = (
                        gmax_data["shiny_url"] if is_shiny else gmax_data["regular_url"]
                    )
                    emoji = (
                        gmax_data["shiny_emoji"]
                        if is_shiny
                        else gmax_data["regular_emoji"]
                    )
                    embed_color = (
                        gmax_data["shiny_color"]
                        if is_shiny
                        else gmax_data["regular_color"]
                    )
                    display_pokemon.append(f"{poke_name}")
                    image_url = sprite
                else:
                    display_pokemon.append(f"{poke_name}")
                    image_url = get_pokemon_gif(poke_name)
            else:
                display_pokemon.append(
                    f"{rarity_emoji} {poke_name}" if rarity_emoji else poke_name
                )
                image_url = get_pokemon_gif(poke_name)
        else:
            image_url = None

        new_embed = discord.Embed(
            title=f"{Emojis.World_boss_Spawn} Special world boss rewards!",
            url=message.jump_url,
            color=embed_color,
        )

        if found_items:
            new_embed.add_field(
                name=f"🎁 Item(s):",
                value="\n".join(f"> {emoji} {name}" for emoji, name in found_items),
                inline=False,
            )
        if display_pokemon:
            new_embed.add_field(
                name=f"🎊 Pokémon:",
                value="\n".join(f"> {poke}" for poke in display_pokemon),
                inline=False,
            )

        if member:
            new_embed.set_author(
                name=member.display_name, icon_url=member.display_avatar.url
            )

        # 🖼️ Thumbnail / Image logic
        if image_url:
            new_embed.set_image(url=get_stable_embed_image_url(image_url))
        elif found_items:
            # Use the first item's emoji as thumbnail if it's a custom emoji
            first_emoji, _ = found_items[0]
            match = re.match(r"<a?:\w+:(\d+)>", str(first_emoji))
            if match:
                emoji_id = match.group(1)
                is_animated = str(first_emoji).startswith("<a:")
                ext = "gif" if is_animated else "png"
                thumb_url = f"https://cdn.discordapp.com/emojis/{emoji_id}.{ext}"
                new_embed.set_thumbnail(url=thumb_url)

        # Footer
        damage_text = ""
        if embed.footer and embed.footer.text:
            dmg_match = re.search(
                r"You dealt ([\d,]+) / ([\d,]+) DMG", embed.footer.text
            )
            if dmg_match:
                damage_text = f"{dmg_match.group(1)}"
        placement_text = ""
        placement_match = re.search(r"You placed (\d+) / (\d+) players", description)
        if placement_match:
            placement_text = f"{placement_match.group(1)}/{placement_match.group(2)}"
        footer_text = (
            f"{challenge_name} | 💥 Damage dealt: {damage_text} | 🏅 Placed: {placement_text}"
            if damage_text or placement_text
            else "💥 Damage dealt: | 🏅 Placed:"
        )
        new_embed.set_footer(
            text=footer_text,
            icon_url=(
                message.guild.icon.url if message.guild and message.guild.icon else None
            ),
        )

        # ✅ Mark as processed so create/edit listeners don't double-post
        _PROCESSED_WB_REWARD_IDS.add(message.id)
        if len(_PROCESSED_WB_REWARD_IDS) > 5000:
            _PROCESSED_WB_REWARD_IDS.clear()

        # Send embed
        log_channel = get_rarespawn_channel(message.guild)
        if log_channel:
            await send_webhook(
                bot=bot,
                channel=log_channel,
                embed=new_embed,
            )
        else:
            if getattr(message, "channel", None):
                await message.channel.send(embed=new_embed)

        pretty_log(
            "success",
            f"Logged special reward for {member.display_name if member else 'unknown'}",
            label="🎁 PokéMeow",
        )

    except Exception as e:
        pretty_log("error", f"Error parsing PokéMeow rewards: {e}", label="🎁 PokéMeow")
        debug_log(f"Exception raised: {e}", highlight=True)

import re

import discord

from Constants.aesthetic import Emojis
from Constants.paldea_galar_dict import dex, rarity_meta
from Constants.pokemons import *
from Constants.vn_allstars_constants import VN_ALLSTARS_EMOJIS
from utils.db.market_value_db import (
    fetch_dex_number_cache,
    fetch_market_value_cache,
    is_pokemon_exclusive_cache,
)
from utils.logs.debug_log import debug_enabled, debug_log, enable_debug
from utils.logs.pretty_log import pretty_log

# ✨───────────────────────────────────────────────
#            📦 Precomputed Lookup Sets
# ✨───────────────────────────────────────────────
7
legendary_set = {mon.lower() for mon in legendary_mons}
superrare_set = {mon.lower() for mon in superrare_mons}
rare_set = {mon.lower() for mon in rare_mons}
uncommon_set = {mon.lower() for mon in uncommon_mons}
common_set = {mon.lower() for mon in common_mons}
exclusive_set = {mon.lower() for mon in exclusive_mons}

# ✨───────────────────────────────────────────────
#            🧹 Name Formatting
# ✨───────────────────────────────────────────────


def format_name_for_pokemons_db_lookup(pokemon_name: str) -> str:
    """Format Pokémon name for market value lookup."""

    if "-o" in pokemon_name:
        debug_log(f"SPECIAL: '-o' detected in name: {pokemon_name!r}")

    if pokemon_name.lower().strip() == "type null":
        debug_log(f"SPECIAL: 'type null' detected: {pokemon_name!r}")

    pokemon_name = pokemon_name.lower().strip()

    # ✨ Strip ID numbers (ex: "#7202")
    pokemon_name = pokemon_name.split("#")[0].strip()

    if pokemon_name.startswith("sgmax "):
        base = pokemon_name[6:].strip()
        return f"shiny gigantamax-{base}"

    if pokemon_name.startswith("gmax "):
        base = pokemon_name[5:].strip()
        return f"gigantamax-{base}"

    if "smega" in pokemon_name:
        return pokemon_name.replace("smega", "shiny mega").replace("-", " ")

    if "mega" in pokemon_name:
        return pokemon_name.replace("-", " ")

    return pokemon_name


def get_dex_number_by_name(name: str) -> int | None:
    """
    Returns the dex number for a given Pokémon name.
    Example: get_dex_number_by_name("flutter-mane") -> 987
    Returns None if not found.
    """

    # Prefer cache lookup first for speed and consistency with market formatting.
    formatted_name = format_names_for_market_value_lookup(name)
    dex_number = fetch_dex_number_cache(formatted_name)
    if dex_number is not None:
        return dex_number

    # Fallback: check static dex mapping.
    for num, poke_name in dex.items():
        if poke_name == name:
            return num

    return None


IN_GAME_MONS_LIST = (
    list(common_mons.keys())
    + list(uncommon_mons.keys())
    + list(rare_mons.keys())
    + list(superrare_mons.keys())
    + list(legendary_mons.keys())
    + list(mega_mons.keys())
    + list(gigantamax_mons.keys())
    + list(shiny_mons.keys())
    + list(shiny_mega_mons.keys())
    + list(shiny_gigantamax_mons.keys())
    + list(golden_mons.keys())
    + list(exclusive_mons.keys())
)

exclusive_mons_list = list(exclusive_mons.keys())


def strip_prefixes(pokemon_name: str):
    """
    Strip form prefixes from a Pokémon name to get the base name for market value lookup.
    Handles prefixes like "Shiny", "Mega", "Gigantamax", "Shiny Mega", etc.
    """
    prefixes = [
        "shiny mega",
        "shiny gigantamax",
        "golden mega",
        "gigantamax",
        "mega",
        "shiny",
        "golden",
    ]
    pokemon_name_lower = pokemon_name.lower()
    for prefix in prefixes:
        for sep in [" ", "-"]:
            if pokemon_name_lower.startswith(prefix + sep):
                return pokemon_name[len(prefix) + 1 :].strip()
    return pokemon_name.strip()


def get_embed_color_by_rarity(pokemon_name: str) -> int:
    rarity = get_rarity(pokemon_name)
    if rarity and rarity in rarity_meta:
        return rarity_meta[rarity]["color"]
    else:
        return 0xFFFFFF  # Default to white if rarity is unknown


def format_price_w_coin(n: int) -> str:
    """Format PokeCoin price with commas (no K/M shorthand)."""
    pokecoin = VN_ALLSTARS_EMOJIS.vna_pokecoin
    return f"{pokecoin} {n:,}"

RARITY_W_LONG_NAME = ["shiny gigantamax", "gigantamax"]

def get_display_name(
    pokemon_name: str, dex: bool = False, is_long_name: bool = False
) -> str:
    """Returns the display name of a Pokémon, optionally including the dex number."""

    rarity = get_rarity(pokemon_name)
    rarity_emoji = rarity_meta.get(rarity, {}).get("emoji", "") if rarity else ""

    # Strip prefixes for display name to avoid clutter (e.g., "Shiny", "Mega", etc.)
    stripped_name = strip_prefixes(pokemon_name)

    if rarity in RARITY_W_LONG_NAME or is_long_name:
        is_long_name = True
    else:
        is_long_name = False

    if is_long_name:
        formatted_name = pokemon_name.title()
    else:
        formatted_name = stripped_name.title()

    display_name = f"{rarity_emoji} {formatted_name}".strip()

    if dex:
        dex_number = get_dex_number_by_name(pokemon_name)
        if dex_number:
            display_name = f"{display_name} #{dex_number}"
    return display_name.strip()


# enable_debug(f"{__name__}.is_mon_exclusive")
def is_mon_exclusive(pokemon: str) -> bool:
    """
    Checks if a given Pokémon is exclusive based on the exclusive_mons list or the market value cache.
    """
    debug_log(f"Checking exclusivity for: {pokemon}")
    name = pokemon.lower()
    if any(name == mon.lower() for mon in exclusive_mons_list):
        debug_log(f"{pokemon} is exclusive based on the exclusive_mons list.")
        return True
    # Check cache for exclusivity, if it's exclusive then it's not auctionable
    pokemon = format_names_for_market_value_lookup(pokemon)
    if is_pokemon_exclusive_cache(pokemon):
        debug_log(f"{pokemon} is exclusive based on the market value cache.")
        return True
    else:
        debug_log(f"{pokemon} is not exclusive based on the market value cache.")
        return False


def get_rarity(pokemon: str):
    """Determines Pokémon rarity from its name."""

    name = pokemon.lower()

    if "golden" in name:
        return "golden"

    if "shiny" in name and "gigantamax" in name:
        return "shiny gigantamax"

    if "shiny" in name and "mega" in name:
        return "shiny mega"

    if "shiny" in name:
        return "shiny"

    if "gigantamax" in name:
        return "gigantamax"

    if "mega" in name and "yanmega" not in name and "meganium" not in name:
        return "mega"

    if name in legendary_set:
        return "legendary"

    if name in superrare_set:
        return "superrare"

    if name in rare_set:
        return "rare"

    if name in uncommon_set:
        return "uncommon"

    if name in common_set:
        return "common"

    return None


def format_names_for_market_value_lookup(pokemon_name: str):
    """
    Format Pokémon name for market value lookup"""
    # Special log for names containing '-o'
    if "-o" in pokemon_name:
        debug_log(f"SPECIAL: '-o' detected in name: {pokemon_name!r}")
    # Special log for 'type null'
    if pokemon_name.lower().strip() == "type null":
        debug_log(f"SPECIAL: 'type null' detected: {pokemon_name!r}")
    pokemon_name = pokemon_name.lower().strip()
    if pokemon_name.startswith("sgmax "):
        # shiny gigantamax-<name>
        base = pokemon_name[6:].strip()
        result = f"shiny gigantamax-{base}"
        # debug_log(f"sgmax result: {result}")
        return result
    elif pokemon_name.startswith("gmax "):
        # gigantamax-<name>
        base = pokemon_name[5:].strip()
        result = f"gigantamax-{base}"
        # debug_log(f"gmax result: {result}")
        return result
    elif "smega" in pokemon_name:
        result = pokemon_name.replace("smega", "shiny mega").replace("-", " ")
        # debug_log(f"smega result: {result}")
        return result
    elif "mega" in pokemon_name:
        result = pokemon_name.replace("-", " ")
        # debug_log(f"mega result: {result}")
        return result
    else:
        # debug_log(f"default result: {pokemon_name}")
        return pokemon_name


def is_mon_in_game(pokemon_name: str) -> bool:
    """Check if a Pokémon is in the game."""
    name_lower = pokemon_name.lower()
    if name_lower in IN_GAME_MONS_LIST:
        return True
    # Fallback to check if the formatted name is in the market value cache
    pokemon_name_formatted = format_names_for_market_value_lookup(pokemon_name)
    market_value = fetch_market_value_cache(pokemon_name_formatted)
    if market_value is not None:
        return True
    return False


def format_discord_timestamp(value):
    if value is None:
        return "N/A"
    if isinstance(value, (int, float)):
        return f"<t:{int(value)}:R>"
    if isinstance(value, str):
        if re.match(r"<t:\d+:R>", value):
            return value
        try:
            num = float(value)
            return f"<t:{int(num)}:R>"
        except ValueError:
            return "N/A"
    return "N/A"


# ✨───────────────────────────────────────────────
#            📝 Get Mon Value
# ✨───────────────────────────────────────────────
async def get_mon_value(bot: discord.Client, pokemon_name: str):
    """Fetch the in-game value of a Pokémon."""
    from utils.db.market_value_db import fetch_market_value_cache

    pokemon_name_formatted = format_name_for_pokemons_db_lookup(pokemon_name)
    pokemon_info = fetch_market_value_cache(pokemon_name_formatted)

    if not isinstance(pokemon_info, dict):
        debug_log(f"No usable market value info for {pokemon_name!r}")
        return None

    raw_price = pokemon_info.get("current_listing")
    has_market_value = bool(raw_price)
    current_listing_price = (
        format_price_w_coin(raw_price) if has_market_value else f"{VN_ALLSTARS_EMOJIS.vna_pokecoin} ?"
    )
    last_seen = format_discord_timestamp(pokemon_info.get("listing_seen"))

    debug_log(
        f"Market value parsed: current_listing={current_listing_price}, "
        f"last_seen={last_seen}, has_market_value={has_market_value}"
    )
    return {
        "current_listing": current_listing_price,
        "last_seen": last_seen,
        "has_market_value": has_market_value,
    }

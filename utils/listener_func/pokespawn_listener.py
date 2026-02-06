import re

import discord

from Constants.clan_wars_constants import CLAN_WARS_ROLES, CLAN_WARS_TEXT_CHANNELS
from Constants.paldea_galar_dict import *
from Constants.variables import PublicChannels, Roles, Server
from Constants.vn_allstars_constants import VN_ALLSTARS_ROLES, VN_ALLSTARS_TEXT_CHANNELS
from utils.functions.webhook_func import send_webhook
from utils.logs.pretty_log import pretty_log

# -------------------- Constants --------------------
AUTO_SPAWN_ROLE_ID = Roles.Spawn_Hunter
AUTO_SPAWN_RARE_ROLE_ID = Roles.Rare_Hunter

# Colors that signify rare Pokémon (legendary/shiny/golden)
LEGENDARY_COLORS = {
    rarity_meta["legendary"]["color"],
    rarity_meta["shiny"]["color"],
    rarity_meta["golden"]["color"],
}


def sentence_case_bold(text: str) -> str:
    """
    Convert a string to sentence case and wrap it in bold markdown.

    Example: "pikachu" -> "**Pikachu**"
    """
    if not text:
        return ""
    sentence_cased = text[0].upper() + text[1:].lower()
    return f"**{sentence_cased}**"


def remove_bold_title_case(text: str) -> str:
    """
    Remove bold markdown from a string and convert it to title case.

    Example: "**pikachu**" -> "Pikachu"
    """
    if not text:
        return ""

    # Remove ** at start and end if present
    if text.startswith("**") and text.endswith("**"):
        text = text[2:-2]

    # Convert to title case
    return text.title()


GUILD_MAP = {
    Server.VNA_ID: {
        "auto_spawn_ping_role_id": VN_ALLSTARS_ROLES.as_spawn_ping,
        "rare_spawn_ping_role_id": VN_ALLSTARS_ROLES.as_rare_spawn_hunter,
        "rare_spawn_channel_id": VN_ALLSTARS_TEXT_CHANNELS.rare_spawn,
    },
    Server.CLAN_WARS_SERVER_ID: {
        "auto_spawn_ping_role_id": CLAN_WARS_ROLES.autospawn_ping,
        "rare_spawn_ping_role_id": CLAN_WARS_ROLES.rare_autospawn_ping,
        "rare_spawn_channel_id": CLAN_WARS_TEXT_CHANNELS.rarespawn,
    },
}


async def as_spawn_ping(bot: discord.Client, message: discord.Message):
    """
    Detects a wild Pokémon spawn in a message and sends the appropriate pings and embeds
    to the configured channels.

    Regular (common/uncommon/rare) Pokémon go to Off-Topic channel with a role ping.
    Paldean, shiny, legendary, golden, or superrare Pokémon also send an embed to the rare spawn channel.

    Args:
        bot (discord.Client): The bot instance.
        message (discord.Message): The Discord message containing the spawn embed.
    """
    # Ignore edited messages or messages without embeds
    if message.edited_at or not message.embeds:
        return

    embed = message.embeds[0]

    # Only proceed if the embed title indicates a wild spawn
    if not (embed.title and "A wild" in embed.title):
        return
    guild = message.guild
    if guild.id not in GUILD_MAP:
        return

    AUTO_SPAWN_ROLE_ID = GUILD_MAP[guild.id]["auto_spawn_ping_role_id"]
    AUTO_SPAWN_RARE_ROLE_ID = GUILD_MAP[guild.id]["rare_spawn_ping_role_id"]
    RARESPAWN_CHANNEL_ID = GUILD_MAP[guild.id]["rare_spawn_channel_id"]

    AUTOSPAWN_PING_ROLE = guild.get_role(AUTO_SPAWN_ROLE_ID)
    RARESPAWN_PING_ROLE = guild.get_role(AUTO_SPAWN_RARE_ROLE_ID)
    RARESPAWN_CHANNEL = guild.get_channel(RARESPAWN_CHANNEL_ID)

    if not AUTOSPAWN_PING_ROLE or not RARESPAWN_PING_ROLE or not RARESPAWN_CHANNEL:
        return

    embed_color = embed.color
    image_url = embed.image.url

    dex_number = None
    rarity_key = "unknown"
    rarity_info = rarity_meta.get("unknown", {})

    # Extract rarity from embed title emoji
    rarity_emoji_match = re.search(r"<:([a-zA-Z0-9_]+):\d+>", embed.title)
    if rarity_emoji_match:
        raw_rarity_key = rarity_emoji_match.group(1).lower()
        rarity_key_map = {
            "common": "common",
            "uncommon": "uncommon",
            "rare": "rare",
            "superrare": "superrare",
            "legendary": "legendary",
            "shiny": "shiny",
            "golden": "golden",
        }
        rarity_key = rarity_key_map.get(raw_rarity_key, "unknown")
        rarity_info = rarity_meta.get(rarity_key, rarity_meta["unknown"])

    # Extract Dex number from embed title emoji
    dex_match = re.search(r"<:([0-9]+):\d+>", embed.title)
    if dex_match:
        dex_number = int(dex_match.group(1))

    # Determine Pokémon name
    if dex_number and dex_number in paldea_galar_dict:
        pokemon_name = sentence_case_bold(paldea_galar_dict[dex_number])
        log_pokemon_name = remove_bold_title_case(pokemon_name)
    else:
        pokemon_name = sentence_case_bold(dex.get(dex_number, "Unknown Pokémon"))
        log_pokemon_name = remove_bold_title_case(pokemon_name)

    shiny_text = "shiny " if rarity_key == "shiny" else ""

    is_paldean = dex_number and dex_number in paldea_galar_dict
    is_legendary_or_rare = embed.color and (
        embed.color.value in LEGENDARY_COLORS
        or embed.color.value == 10364899  # legendary alt color
    )

    # -------------------- Regular auto-spawn --------------------
    if not (is_paldean or is_legendary_or_rare):
        # Only ping AS Channel channel
        emoji = rarity_info.get("emoji", "❓")
        content = f"{AUTOSPAWN_PING_ROLE} A wild {emoji} {pokemon_name} has appeared!"

        await send_webhook(
            bot,
            content=content,
            channel=message.channel,
        )
        pretty_log(
            message=f"Auto-spawn ping sent: {log_pokemon_name} in #{message.channel.name}",
            tag="sent",
        )

        return

    # -------------------- Rare / shiny / Paldean spawn --------------------
    content = f"{RARESPAWN_PING_ROLE} A wild {shiny_text}{rarity_info.get('emoji', '❓')} {pokemon_name} has appeared!"

    await send_webhook(
        bot,
        content=content,
        channel=message.channel,
    )
    pretty_log(
        message=f"Rare spawn ping sent: {shiny_text}{log_pokemon_name} in #{message.channel.name}",
        tag="sent",
    )

    # Send embed to rare spawn channel
    message_link = f"https://discord.com/channels/{message.guild.id}/{message.channel.id}/{message.id}"
    desc = f"A wild {rarity_info['emoji']} {pokemon_name} has spawned!"
    footer_text = f"Spawned in {message.guild.name}"
    footer_icon = message.guild.icon.url

    rare_spawn_embed = discord.Embed(
        title=desc, url=message.jump_url, color=embed_color
    )
    rare_spawn_embed.set_image(url=image_url)
    rare_spawn_embed.set_footer(text=footer_text, icon_url=footer_icon)

    rare_spawn_channel = RARESPAWN_CHANNEL
    if rare_spawn_channel:
        # await rare_spawn_channel.send(embed=rare_spawn_embed)
        await send_webhook(
            bot,
            embed=rare_spawn_embed,
            channel=rare_spawn_channel,
        )

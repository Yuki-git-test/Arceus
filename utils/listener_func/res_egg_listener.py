import re

import discord

from Constants.aesthetic import Emojis
from Constants.vn_allstars_constants import (
    MEANIES_RARESPAWN_CHANNEL,
    VN_ALLSTARS_EMOJIS,
    VN_ALLSTARS_TEXT_CHANNELS,
    VNA_SERVER_ID,
    YUKI_SERVER_ID,
    KHY_BOT_SERVER,
    KHY_BOT_SERVER_RS,
)
from Constants.clan_wars_constants import CLAN_WARS_TEXT_CHANNELS, CLAN_WARS_SERVER_ID
from utils.functions.pokemon_func import get_dex_number_by_name, get_mon_value
from utils.functions.webhook_func import send_webhook
from utils.logs.debug_log import debug_log, enable_debug

# enable_debug(f"{__name__}.handle_res_egg_hatch")
RARE_EGG_EXCLUSIVES = [
    "chingling",
    "mimejr",
    "happiny",
    "chatot",
    "munchlax",
    "riolu",
    "audino",
    "zorua",
    "emolga",
    "ferroseed",
    "golett",
    "pawniard",
    "pancham",
    "spritzee",
    "swirlix",
    "noibat",
    "crabrawler",
    "rockruff",
    "type-null",
    "yamper",
    "nickit",
]
SUPER_RARE_EGG_EXCLUSIVE = ["carbink", "mimikyu"]


def get_rarespawn_channel(guild: discord.Guild):
    if guild.id == VNA_SERVER_ID:
        return guild.get_channel(VN_ALLSTARS_TEXT_CHANNELS.rare_spawn)
    if guild.id == YUKI_SERVER_ID:
        return guild.get_channel(MEANIES_RARESPAWN_CHANNEL)
    if guild.id == CLAN_WARS_SERVER_ID:
        return guild.get_channel(CLAN_WARS_TEXT_CHANNELS.rarespawn)
    if guild.id == KHY_BOT_SERVER:
        return guild.get_channel(KHY_BOT_SERVER_RS)
    else:
        return guild.get_channel(VN_ALLSTARS_TEXT_CHANNELS.rare_spawn)  # Fallback to VNA rare spawn channel

def extract_hatch_info(message: str) -> dict | None:
    match = re.search(
        r"\*\*(.+?)\*\* hatched in \*\*(.+?)\*\*!.*?" r"\*\*(.+?)\*\*",
        message,
        re.DOTALL,
    )

    if not match:
        return None

    return {
        "egg_type": match.group(1),
        "incubator_num": match.group(2),
        "hatched_mon": match.group(3),
    }


async def handle_res_egg_hatch(bot: discord.Client, message: discord.Message):
    debug_log(
        f"Processing res egg hatch message {message.id} in guild "
        f"{getattr(message.guild, 'id', None)}."
    )
    embed = message.embeds[0] if message.embeds else None
    if not embed:
        debug_log("No embed found; ignoring message.")
        return
    debug_log(f"Using embed with title: {embed.title!r}")

    hatch_info = extract_hatch_info(embed.description)
    if not hatch_info:
        debug_log("Could not extract hatch information from the embed description.")
        return
    debug_log(f"Extracted hatch information: {hatch_info}")

    embed_color = embed.color
    embed_image_url = embed.image.url if embed.image else None
    embed_author_text = embed.author.name if embed.author else None
    embed_author_icon_url = embed.author.icon_url if embed.author else None

    egg_type = hatch_info["egg_type"]
    hatched_mon = hatch_info["hatched_mon"]
    incubator_num = hatch_info["incubator_num"]

    if (
        hatched_mon.lower() not in RARE_EGG_EXCLUSIVES
        and hatched_mon.lower() not in SUPER_RARE_EGG_EXCLUSIVE
        and "shiny" not in hatched_mon.lower()
        and "golden" not in hatched_mon.lower()
    ):
        debug_log(f"{hatched_mon} is not a rare, shiny, or golden hatch; ignoring it.")
        return

    if hatched_mon.lower() in RARE_EGG_EXCLUSIVES:
        display_name = f"{VN_ALLSTARS_EMOJIS.vna_rare} {hatched_mon.title()}"
    elif hatched_mon.lower() in SUPER_RARE_EGG_EXCLUSIVE:
        display_name = f"{VN_ALLSTARS_EMOJIS.vna_superrare} {hatched_mon.title()}"
    elif "shiny" in hatched_mon.lower():
        # Remove Shiny from the name for display
        clean_name = hatched_mon.lower().replace("shiny", "").strip()
        display_name = f"{VN_ALLSTARS_EMOJIS.vna_shiny} {clean_name.title()}"
    elif "golden" in hatched_mon.lower():
        # Remove Golden from the name for display
        clean_name = hatched_mon.lower().replace("golden", "").strip()
        display_name = f"{VN_ALLSTARS_EMOJIS.vna_golden} {clean_name.title()}"
    else:
        display_name = hatched_mon.title()
    debug_log(f"Preparing rare-spawn announcement for {hatched_mon} as {display_name}.")

    dex_number = get_dex_number_by_name(hatched_mon)
    rarespawn_channel_obj = get_rarespawn_channel(message.guild)
    if not rarespawn_channel_obj:
        debug_log(
            f"Rare-spawns channel was not found for guild {message.guild.id}."
        )

    rs_embed = discord.Embed(
        title=f"**{egg_type.title()}** hatched in **{incubator_num.title()}**",
        url=message.jump_url,
        description=f"{display_name} #{dex_number}\n\u200b",
        color=embed_color,
    )

    if embed_image_url:
        rs_embed.set_image(url=embed_image_url)
    if embed_author_text:
        rs_embed.set_author(name=embed_author_text, icon_url=embed_author_icon_url)

    mon_value = await get_mon_value(bot, hatched_mon)
    if mon_value and mon_value.get("has_market_value"):
        last_seen = mon_value.get("last_seen")
        last_seen_text = f"Value as of {last_seen}" if last_seen != "N/A" else "Value"
        current_listing = mon_value.get("current_listing")
        rs_embed.add_field(name=last_seen_text, value=current_listing, inline=False)
        debug_log(f"Added market value to announcement: {current_listing!r}.")
    else:
        debug_log(f"No market value available for {hatched_mon}.")

    debug_log(f"Sending rare-spawn announcement to channel {rarespawn_channel_obj}.")
    rs_embed.set_footer(
        text=f"Hatched in {message.guild.name}",
        icon_url=message.guild.icon.url if message.guild.icon else None,
    )
    await send_webhook(bot=bot, channel=rarespawn_channel_obj, embed=rs_embed)
    debug_log(f"Rare-spawn announcement sent for {hatched_mon}.")

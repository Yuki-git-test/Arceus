import re

import discord

#If colors are different just check terminal and update the one in rarity_meta
from Constants.paldea_galar_dict import get_rarity_by_color, rarity_meta, Legendary_icon_url
from utils.logs.pretty_log import pretty_log
from vn_allstars_constants import (
    VN_ALLSTARS_EMOJIS,
    VN_ALLSTARS_ROLES,
    VN_ALLSTARS_TEXT_CHANNELS,
)

# 🟣────────────────────────────────────────────
#  ⚡ Market Snipe ⚡
# 🟣────────────────────────────────────────────
MH_WEBHOOK_IDS = {
    1425808727793205378,  # Golden
    1425808602722996327,  # Shiny
    1425808333180371088,  # Legendary, Mega , Gmax
    1425808079588425740,  # CURS
}
SNIPE_MAP = {
    "common": {"role": VN_ALLSTARS_ROLES.common_snipe},
    "uncommon": {"role": VN_ALLSTARS_ROLES.uncommon_snipe},
    "rare": {"role": VN_ALLSTARS_ROLES.rare_snipe},
    "superrare": {"role": VN_ALLSTARS_ROLES.super_rare_snipe},
    "legendary": {"role": VN_ALLSTARS_ROLES.legendary_snipe},
    "shiny": {"role": VN_ALLSTARS_ROLES.shiny_snipe},
    "golden": {"role": VN_ALLSTARS_ROLES.golden_snipe},
    "event_exclusive": {"role": VN_ALLSTARS_ROLES.eventexclusives_snipe},
    "gmax": {"role": VN_ALLSTARS_ROLES.gmax_snipe},
    "mega": {"role": VN_ALLSTARS_ROLES.mega_snipe},
}

SNIPE_CHANNEL_ID = VN_ALLSTARS_TEXT_CHANNELS.snipe_channel


async def market_snipe(message: discord.Message):
    """"""
    if message.webhook_id not in MH_WEBHOOK_IDS:
        pretty_log("debug", f"Message from unallowed webhook: {message.webhook_id}")
        return

    if not message.embeds:
        pretty_log("debug", "Message has no embeds")
        return

    embed = message.embeds[0]
    embed_author_name = embed.author.name if embed.author else ""

    match = re.match(r"(.+?)\s+#(\d+)", embed_author_name)
    if not match:
        pretty_log("debug", f"Could not parse embed author name: {embed_author_name}")
        return

    poke_name = match.group(1)
    poke_dex = int(match.group(2))
    fields = {f.name: f.value for f in embed.fields}

    # Extract Listed Price and Lowest Market, removing any emojis
    listed_price_str = re.sub(r"<a?:\w+:\d+>", "", fields.get("Listed Price", "0"))
    match_price = re.search(r"(\d[\d,]*)", listed_price_str)
    listed_price = int(match_price.group(1).replace(",", "")) if match_price else 0
    lowest_market_str = re.sub(r"<a?:\w+:\d+>", "", fields.get("Lowest Market", "0"))
    lowest_market_match = re.search(r"(\d[\d,]*)", lowest_market_str)
    lowest_market = (
        int(lowest_market_match.group(1).replace(",", "")) if lowest_market_match else 0
    )

    original_id = fields.get("ID", "0")
    embed_color = embed.color.value
    display_pokemon_name = poke_name.title()

    pretty_log(
        "info",
        f"Parsed Message - Name: {poke_name}, Dex: {poke_dex}, Listed: {listed_price}, Lowest: {lowest_market}, ID: {original_id}, Color: {embed_color}",
    )

    # If Listed Price is 30% or more below Lowest Market, it's a snipe
    if lowest_market > 0 and listed_price <= lowest_market * 0.7:
        pretty_log(
            "info",
            f"Snipe detected! {poke_name} #{poke_dex} listed for {listed_price} (Lowest Market: {lowest_market})",
        )
        # Here you can add code to notify users, log the snipe, etc.
        rarity = get_rarity_by_color(embed_color)
        pretty_log("debug", f"Color {embed_color} detected as rarity: {rarity}")

        if rarity == "unknown":

            if (
                "shiny gigantamax-" in poke_name.lower()
                or "shiny eternamax-" in poke_name.lower()
                or "shiny mega " in poke_name.lower()
            ):
                rarity = "shiny"
            elif "mega " in poke_name.lower():
                rarity = "mega"
            elif (
                "gigantamax-" in poke_name.lower() or "eternamax-" in poke_name.lower()
            ):
                rarity = "gmax"
            elif embed.author and embed.author.icon_url == Legendary_icon_url:
                rarity = "legendary"

        ping_role_id = SNIPE_MAP.get(rarity, {}).get("role")
        pretty_log("debug", f"Final rarity: {rarity}, Role ID: {ping_role_id}")

        if ping_role_id:
            snipe_channel = message.guild.get_channel(SNIPE_CHANNEL_ID)
            if snipe_channel:
                content = f"<@&{ping_role_id}> {display_pokemon_name} listed for {VN_ALLSTARS_EMOJIS.vna_pokecoin} {listed_price:,}!"

                # 🧾 Build embed
                new_embed = discord.Embed(color=embed.color or 0x0855FB)
                if embed.thumbnail:
                    new_embed.set_thumbnail(url=embed.thumbnail.url)
                new_embed.set_author(
                    name=embed_author_name,
                    icon_url=embed.author.icon_url if embed.author else None,
                )
                new_embed.add_field(name="ID", value=original_id, inline=True)
                new_embed.add_field(
                    name="Listed Price",
                    value=f"{VN_ALLSTARS_EMOJIS.vna_pokecoin} {listed_price_str}",
                    inline=True,
                )
                new_embed.add_field(
                    name="Amount", value=fields.get("Amount", "1"), inline=True
                )
                new_embed.add_field(
                    name="Lowest Market",
                    value=f"{VN_ALLSTARS_EMOJIS.vna_pokecoin} {lowest_market_str}",
                    inline=True,
                )

                new_embed.add_field(
                    name="Listing Seen", value=fields.get("Listing Seen", "N/A"), inline=True
                )

                new_embed.set_footer(
                    text="Kindly check market listing before purchasing.",
                    icon_url=message.guild.icon.url if message.guild else None,
                )
                await snipe_channel.send(content=content, embed=new_embed)

                pretty_log(
                    "info",
                    f"Snipe notification sent in channel {snipe_channel.name} for {display_pokemon_name} at {listed_price:,}",
                )

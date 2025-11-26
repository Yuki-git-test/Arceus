import asyncio
import re

import discord

# If colors are different just check terminal and update the one in rarity_meta
from Constants.paldea_galar_dict import (
    Legendary_icon_url,
    get_rarity_by_color,
    rarity_meta,
)
from utils.cache.cache_list import _market_alert_index, market_alert_cache
from utils.logs.debug_log import debug_log, enable_debug
from utils.logs.pretty_log import pretty_log
from vn_allstars_constants import (
    VN_ALLSTARS_EMOJIS,
    VN_ALLSTARS_ROLES,
    VN_ALLSTARS_TEXT_CHANNELS,
)

#enable_debug(f"{__name__}.market_snipe_handler")
#enable_debug(f"{__name__}.handle_market_alert")
#enable_debug(f"{__name__}.market_feeds_listener")
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

processed_market_feed_message_ids = set()
processed_snipe_ids = set()


# 🟣────────────────────────────────────────────
#           👂 Market Snipe Handler
# 🟣────────────────────────────────────────────
async def market_snipe_handler(
    poke_name: str,
    listed_price: int,
    id: str,
    lowest_market: int,
    amount: int,
    listing_seen: str,
    guild: discord.Guild,
    embed: discord.Embed,
):
    embed_color = embed.color.value
    rarity = get_rarity_by_color(embed_color)
    display_pokemon_name = poke_name.title()

    if rarity == "unknown":
        if (
            "shiny gigantamax-" in poke_name.lower()
            or "shiny eternamax-" in poke_name.lower()
            or "shiny mega " in poke_name.lower()
        ):
            rarity = "shiny"
        elif "mega " in poke_name.lower():
            rarity = "mega"
        elif "gigantamax-" in poke_name.lower() or "eternamax-" in poke_name.lower():
            rarity = "gmax"
        elif embed.author and embed.author.icon_url == Legendary_icon_url:
            rarity = "legendary"

    ping_role_id = SNIPE_MAP.get(rarity, {}).get("role")
    if ping_role_id:
        snipe_channel = guild.get_channel(SNIPE_CHANNEL_ID)
        if snipe_channel:
            content = f"<@&{ping_role_id}> {display_pokemon_name} listed for {VN_ALLSTARS_EMOJIS.vna_pokecoin} {listed_price:,}!"

            # 🧾 Build embed
            new_embed = discord.Embed(color=embed.color or 0x0855FB)
            if embed.thumbnail:
                new_embed.set_thumbnail(url=embed.thumbnail.url)
            new_embed.set_author(
                name=embed.author.name if embed.author else "",
                icon_url=embed.author.icon_url if embed.author else None,
            )
            new_embed.add_field(name="Buy Command", value=f";m b {id}", inline=False)
            new_embed.add_field(name="ID", value=id, inline=True)
            new_embed.add_field(
                name="Listed Price",
                value=f"{VN_ALLSTARS_EMOJIS.vna_pokecoin} {listed_price:,}",
                inline=True,
            )
            new_embed.add_field(name="Amount", value=str(amount), inline=True)
            new_embed.add_field(
                name="Lowest Market",
                value=f"{VN_ALLSTARS_EMOJIS.vna_pokecoin} {lowest_market:,}",
                inline=True,
            )

            new_embed.add_field(
                name="Listing Seen",
                value=listing_seen,
                inline=True,
            )

            new_embed.set_footer(
                text="Kindly check market listing before purchasing.",
                icon_url=guild.icon.url if guild else None,
            )
            await snipe_channel.send(content=content, embed=new_embed)

            pretty_log(
                "sent",
                f"Snipe notification sent in channel {snipe_channel.name} for {display_pokemon_name} at {listed_price:,}",
            )


# 🟣────────────────────────────────────────────
#        👂 Market Alert Handler
# 🟣────────────────────────────────────────────
async def handle_market_alert(
    user_name: str,
    guild: discord.Guild,
    original_id: str,
    poke_name: str,
    listed_price: int,
    channel_id: int,
    role_id: int,
    amount: int,
    lowest_market: int,
    listing_seen: str,
    embed: discord.Embed,
):

    alert_channel = guild.get_channel(channel_id)
    if not alert_channel:
        pretty_log(
            "error",
            f"Alert channel with ID {channel_id} not found in guild {guild.name}",
        )
        return

    # Build embed
    color = embed.color or 0x00FF00
    alert_embed = discord.Embed(color=color)
    if embed.thumbnail:
        alert_embed.set_thumbnail(url=embed.thumbnail.url)
    alert_embed.set_author(
        name=embed.author.name if embed.author else "",
        icon_url=embed.author.icon_url if embed.author else None,
    )

    # Buy command
    alert_embed.add_field(name="Buy Command", value=f";m b {original_id}", inline=False)
    alert_embed.add_field(name="ID", value=original_id, inline=True)
    alert_embed.add_field(
        name="Listed Price",
        value=f"{VN_ALLSTARS_EMOJIS.vna_pokecoin} {listed_price:,}",
        inline=True,
    )
    alert_embed.add_field(name="Amount", value=amount, inline=True)
    alert_embed.add_field(
        name="Lowest Market",
        value=f"{VN_ALLSTARS_EMOJIS.vna_pokecoin} {lowest_market:,}",
        inline=True,
    )
    alert_embed.add_field(
        name="Listing Seen",
        value=listing_seen,
        inline=True,
    )
    alert_embed.set_footer(
        text="Kindly check market listing before purchasing.",
        icon_url=guild.icon.url if guild else None,
    )
    if role_id:
        content = f"<@&{role_id}> {poke_name.title()} listed for {VN_ALLSTARS_EMOJIS.vna_pokecoin} {listed_price:,} each!"
    else:
        content = f"{poke_name.title()} listed for {VN_ALLSTARS_EMOJIS.vna_pokecoin} {listed_price:,} each!"
    await alert_channel.send(content=content, embed=alert_embed)
    pretty_log(
        "sent",
        f"Market alert sent in channel {alert_channel.name} for {user_name} {poke_name.title()} at {listed_price:,}",
    )


# 🟣────────────────────────────────────────────
#           👂 Market Feeds Listener
# 🟣────────────────────────────────────────────
async def market_feeds_listener(message: discord.Message):
    """
    Listens for market listings and detects potential snipes.
    """
    debug_log(
        f"Received message with ID: {message.id} from webhook: {message.webhook_id}"
    )
    if message.webhook_id not in MH_WEBHOOK_IDS:
        debug_log(f"Message from unallowed webhook: {message.webhook_id}")
        return

    if not message.embeds:
        debug_log("Message has no embeds")
        return

    if message.id in processed_market_feed_message_ids:
        debug_log(f"Message ID {message.id} already processed")
        return
    processed_market_feed_message_ids.add(message.id)

    for embed in message.embeds:
        try:
            embed_author_name = embed.author.name if embed.author else ""
            debug_log(f"Processing embed with author: {embed_author_name}")

            match = re.match(r"(.+?)\s+#(\d+)", embed_author_name)
            if not match:
                debug_log(f"Could not parse embed author name: {embed_author_name}")
                continue

            poke_name = match.group(1)
            poke_dex = int(match.group(2))
            debug_log(f"Parsed poke_name: {poke_name}, poke_dex: {poke_dex}")

            fields = {f.name: f.value for f in embed.fields}
            debug_log(f"Embed fields: {fields}")

            # Extract Listed Price and Lowest Market, removing any emojis
            listed_price_str = re.sub(
                r"<a?:\w+:\d+>", "", fields.get("Listed Price", "0")
            )
            match_price = re.search(r"(\d[\d,]*)", listed_price_str)
            listed_price = (
                int(match_price.group(1).replace(",", "")) if match_price else 0
            )
            debug_log(f"Parsed listed_price: {listed_price}")

            lowest_market_str = re.sub(
                r"<a?:\w+:\d+>", "", fields.get("Lowest Market", "0")
            )
            lowest_market_match = re.search(r"(\d[\d,]*)", lowest_market_str)
            lowest_market = (
                int(lowest_market_match.group(1).replace(",", ""))
                if lowest_market_match
                else 0
            )
            debug_log(f"Parsed lowest_market: {lowest_market}")

            listing_seen = fields.get("Listing Seen", "N/A")
            amount = fields.get("Amount", "1")
            debug_log(f"Parsed listing_seen: {listing_seen}, amount: {amount}")

            original_id = fields.get("ID", "0")
            embed_color = embed.color.value
            display_pokemon_name = poke_name.title()

            # If Listed Price is 30% or more below Lowest Market, it's a snipe
            if lowest_market > 0 and listed_price <= lowest_market * 0.7:
                debug_log(
                    f"Snipe detected for {poke_name} at price {listed_price} (lowest market: {lowest_market})"
                )
                if original_id in processed_snipe_ids:
                    debug_log(f"Snipe ID {original_id} already processed")
                    continue

                processed_snipe_ids.add(original_id)

                await market_snipe_handler(
                    poke_name=poke_name,
                    listed_price=listed_price,
                    id=original_id,
                    lowest_market=lowest_market,
                    amount=int(amount),
                    listing_seen=listing_seen,
                    guild=message.guild,
                    embed=embed,
                )

            # Check for market alerts
            if not market_alert_cache:
                debug_log("Market alert cache is empty, skipping alert checks.")
                continue  # Skip if cache is empty

            # ✅ O(1) lookup using indexed cache
            alerts_to_check = [
                alert
                for key, alert in _market_alert_index.items()
                if key[0].lower() == poke_name.lower()
            ]
            debug_log(f"Alerts to check: {alerts_to_check}")

            for alert in alerts_to_check:
                debug_log(
                    f"Checking alert for user {alert['user_name']} and pokemon {alert['pokemon']}"
                )
                if (
                    alert["pokemon"].lower() == poke_name.lower()
                    and listed_price <= alert["max_price"]
                ):
                    role_id = alert["role_id"]
                    channel_id = alert["channel_id"]
                    user_name = alert["user_name"]

                    debug_log(
                        f"Triggering market alert for {user_name} on {poke_name} at price {listed_price}"
                    )
                    await handle_market_alert(
                        user_name=user_name,
                        guild=message.guild,
                        original_id=original_id,
                        poke_name=poke_name,
                        listed_price=listed_price,
                        channel_id=channel_id,
                        role_id=role_id,
                        amount=amount,
                        lowest_market=lowest_market,
                        listing_seen=listing_seen,
                        embed=embed,
                    )
        except Exception as e:
            debug_log(f"Exception in embed processing: {e}", highlight=True, force=True)

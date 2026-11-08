from datetime import datetime
import re

import discord

from Constants.vn_allstars_constants import DEFAULT_EMBED_COLOR
from Constants.paldea_galar_dict import rarity_meta
from utils.pokemeow.get_pokemeow_reply import get_pokemeow_reply_or_interaction_member
from utils.functions.pokemon_func import get_dex_number_by_name, get_mon_value
from utils.functions.webhook_func import send_webhook
from utils.logs.debug_log import debug_log
from utils.logs.debug_log import debug_log
from utils.logs.pretty_log import pretty_log
from utils.listener_func.res_egg_listener import get_rarespawn_channel

def extract_bold_text(message: str) -> str | None:
    match = re.search(r"\*\*([^*]+)\*\*!$", message)
    return match.group(1) if match else None


async def promo_claim_listener(bot: discord.Client, message: discord.Message):
    member = await get_pokemeow_reply_or_interaction_member(message=message)
    if not member:
        return

    embed = message.embeds[0] if message.embeds else None
    if not embed:
        return
    embed_description = embed.description if embed.description else ""
    claimed_promo = extract_bold_text(embed_description)
    if not claimed_promo:
        return
    image_url = embed.image.url if embed.image else None

    pretty_log(f"Claimed promo: Golden {claimed_promo} by member: {member}")

    # Get Golden emoji and color
    golden = rarity_meta.get("golden", {})

    golden_emoji = golden.get("emoji")
    golden_color = golden.get("color")
    raw_golden_name = f"golden {claimed_promo}"
    dex_number = get_dex_number_by_name(raw_golden_name)

    dex_suffix = f" #{dex_number}" if dex_number is not None else ""
    display_promo_name = (
        f"{golden_emoji} {claimed_promo.title()}{dex_suffix}"
        if golden_emoji
        else f"Golden {claimed_promo.title()}{dex_suffix}"
    )

    claim_embed = discord.Embed(
        title="Promo Claimed",
        url=message.jump_url,
        description=f"{member.mention} has claimed **{display_promo_name}**\n\u200b",
        color=golden_color if golden_color else DEFAULT_EMBED_COLOR,
        timestamp=datetime.now(),
    )
    claim_embed.set_author(
        name=member.display_name, icon_url=member.avatar.url if member.avatar else None
    )
    if image_url:
        claim_embed.set_image(url=image_url)
    claim_embed.set_footer(
        text=f"Claimed in {message.guild.name}",
        icon_url=message.guild.icon.url if message.guild and message.guild.icon else None,
    )
    mon_value = await get_mon_value(bot, raw_golden_name)
    if mon_value and mon_value.get("has_market_value"):
        last_seen = mon_value.get("last_seen")
        last_seen_text = (
            f"Value as of {last_seen}" if last_seen != "N/A" else "Value"
        )
        current_listing = mon_value.get("current_listing")
        claim_embed.add_field(name=last_seen_text, value=current_listing, inline=False)
        debug_log(f"Added market value to announcement: {current_listing!r}.")
    else:
        debug_log(f"No market value available for {raw_golden_name}.")
    debug_log(f"Sending promo claim embed for {raw_golden_name} to rare spawn channel.")
    rarespawn_channel = get_rarespawn_channel(message.guild)
    await send_webhook(
        bot=bot, content=None, embed=claim_embed, channel=rarespawn_channel
    )

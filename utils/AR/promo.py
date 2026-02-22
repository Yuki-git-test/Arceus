import discord

from Constants.vn_allstars_constants import ARCEUS_EMBED_COLOR
from utils.db.promo_team import get_promo_team
from utils.functions.pokemon_func import get_display_name
from utils.logs.pretty_log import pretty_log


async def build_promo_embed(bot: discord.Client, guild: discord.Guild) -> discord.Embed | None:
    promo_team_data = await get_promo_team(bot)
    if not promo_team_data:
        pretty_log(
            "info",
            "No promo team data found in database. Cannot send promo team embed.",
        )
        return None
    instructions = promo_team_data["instructions"]
    image_link = promo_team_data["image_link"]
    thumbnail_link = promo_team_data["thumbnail_link"]
    promo_mon = promo_team_data["promo_mon"]
    egg_mon = promo_team_data["egg_mon"]
    promo_mon_display = get_display_name(promo_mon) if promo_mon else "N/A"
    egg_mon_display = get_display_name(egg_mon) if egg_mon else "N/A"
    ends_on = promo_team_data["ends_on"]
    ends_on_str = ""
    if ends_on:
        ends_on_str = f"\n🗓️ Promo ends on <t:{ends_on}:f>"
    topline = f"""# PROMO INFO
POKEMON: {promo_mon_display}
EGG: {egg_mon_display}
COMMANDS:"""
    desc = f"{topline}\n{instructions}\n{ends_on_str}"
    embed = discord.Embed(
        description=desc,
        color=ARCEUS_EMBED_COLOR,
    )
    embed.set_image(url=image_link) if image_link else None
    embed.set_thumbnail(url=thumbnail_link) if thumbnail_link else None
    embed.set_footer(
        text="To use this command, type !promo in any channel.",
        icon_url=(
            guild.icon.url if guild and guild.icon else None
        ),
    )
    return embed

async def promo_team(bot: discord.Client, message: discord.Message):

    embed = await build_promo_embed(bot, message.guild)
    if not embed:
        pretty_log(
            "info",
            "No promo team embed could be built. Not sending message.",
        )
        return

    try:
        await message.reply(embed=embed, mention_author=False)
        pretty_log(
            "info",
            f"Sent promo team embed",
        )
    except Exception as e:
        pretty_log(
            "warn",
            f"Failed to send promo team embed: {e}",
        )
    

import discord
from utils.db.promo_team import get_promo_mon, upsert_promo_team
from utils.logs.pretty_log import pretty_log

async def promo_team_listener(bot: discord.Client, message: discord.Message):
    embed = message.embeds[0] if message.embeds else None
    if not embed:
        return

    # Check if there is a promo team in the database
    old_promo_mon = await get_promo_mon(bot)
    if old_promo_mon:
        return

    instructions = embed.description
    image_link = embed.image.url if embed.image else None
    thumbnail_link = embed.thumbnail.url if embed.thumbnail else None

    # Check fields for promo mon and egg mon
    promo_mon = None
    egg_mon = None
    for field in embed.fields:
        if "promo pokemon" in field.name.lower():
            promo_mon = field.value
        elif "promo egg" in field.name.lower():
            egg_mon = field.value

    if not promo_mon and not egg_mon:
        return

    # Upsert the promo team into the database
    await upsert_promo_team(
        bot,
        promo_mon=promo_mon,
        egg_mon=egg_mon,
        instructions=instructions,
        image_link=image_link,
        thumbnail_link=thumbnail_link,
    )

    # Add a reaction to indicate the promo team was saved
    try:
        await message.add_reaction("✅")
    except Exception as e:
        pretty_log(
            "warn",
            f"Failed to add reaction to promo team message: {e}",
        )
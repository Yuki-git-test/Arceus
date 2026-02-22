import discord

from utils.db.promo_team import get_promo_mon, upsert_promo_team, delete_promo_team
from utils.logs.debug_log import debug_log, enable_debug
from utils.logs.pretty_log import pretty_log
from utils.functions.pokemon_func import get_display_name
from Constants.vn_allstars_constants import VN_ALLSTARS_ROLES
from utils.AR.promo import build_promo_embed
enable_debug(f"{__name__}.promo_team_listener")
async def promo_team_listener(bot: discord.Client, message: discord.Message):
    debug_log(f"Received message in promo_team_listener: {message.id}")
    embed = message.embeds[0] if message.embeds else None
    if not embed:
        debug_log("No embed found in message.")
        return
    # Check fields for promo mon and egg mon
    promo_mon = None
    egg_mon = None
    for field in embed.fields:
        debug_log(f"Checking embed field: {field.name} -> {field.value}")
        if "promo pokemon" in field.name.lower():
            promo_mon = field.value
            debug_log(f"Found promo_mon: {promo_mon}")
        elif "promo egg" in field.name.lower():
            egg_mon = field.value
            debug_log(f"Found egg_mon: {egg_mon}")

    footer_text = embed.footer.text if embed.footer else None
    if not promo_mon and not egg_mon:
        debug_log("No promo_mon or egg_mon found in embed fields. Exiting listener.")
        return
    # Check if there is a promo team in the database
    old_promo_mon = await get_promo_mon(bot)
    debug_log(f"Old promo mon: {old_promo_mon}")
    if old_promo_mon == promo_mon and footer_text != "news_post":
        debug_log("Promo mon in DB matches new promo mon and footer is not news_post. No update needed.")
        return

    if old_promo_mon and old_promo_mon != promo_mon:
        debug_log("Existing promo mon found in DB that differs from new promo mon. Deleting old promo team.")
        await delete_promo_team(bot)

        instructions = embed.description
        image_link = embed.image.url if embed.image else None
        thumbnail_link = embed.thumbnail.url if embed.thumbnail else None
        debug_log(f"Embed description: {instructions}")
        debug_log(f"Image link: {image_link}")
        debug_log(f"Thumbnail link: {thumbnail_link}")

        pretty_log(
            "info",
            f"Footer text: {footer_text}",
        )


        # Upsert the promo team into the database
        debug_log(f"Upserting promo team: promo_mon={promo_mon}, egg_mon={egg_mon}, instructions={instructions}, image_link={image_link}, thumbnail_link={thumbnail_link}")
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
            debug_log("Added ✅ reaction to promo team message.")
        except Exception as e:
            debug_log(f"Failed to add reaction: {e}")
            pretty_log(
                "warn",
                f"Failed to add reaction to promo team message: {e}",
            )

        if footer_text and footer_text == "news_post":
            promo_embed = await build_promo_embed(bot, message.guild)

            meow_promo_role = message.guild.get_role(VN_ALLSTARS_ROLES.meow_promo)
            promo_mon_display = get_display_name(promo_mon) if promo_mon else "N/A"
            annoucement_channel = message.guild.get_channel(VN_ALLSTARS_ROLES.announcments)
            content = f"{meow_promo_role.mention if meow_promo_role else ''} Team for {promo_mon_display}!"
            if annoucement_channel:
                try:
                    await annoucement_channel.send(content=content, embed=promo_embed)
                    debug_log(f"Sent promo team announcement in {annoucement_channel.name}")
                except Exception as e:
                    debug_log(f"Failed to send promo team announcement: {e}")
                    pretty_log(
                        "warn",
                        f"Failed to send promo team announcement: {e}",
                    )


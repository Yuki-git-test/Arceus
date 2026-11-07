import re
from datetime import datetime

import discord

from utils.listener_func.res_egg_listener import get_rarespawn_channel

from Constants.paldea_galar_dict import rarity_meta
from utils.functions.pokemon_func import get_display_name
from utils.functions.webhook_func import send_webhook
from utils.logs.pretty_log import pretty_log
from utils.logs.debug_log import debug_log
from utils.visuals.get_pokemon_gif import get_pokemon_gif

def extract_from_battle_message(content: str) -> dict:
    """
    Extract username and Pokemon reward from a battle result message.

    Args:
        content: The battle message content

    Returns:
        Dictionary with extracted data:
        {
            "username": str or None,
            "pokemon_reward": str or None
        }
    """
    username = None
    pokemon_reward = None

    # Extract username from "**username** won the battle" pattern
    username_match = re.search(
        r"(?:\*\*)?([^\n*<>]+?)(?:\*\*)?\s+won\s+the\s+battle", content, re.IGNORECASE
    )
    if username_match:
        username = username_match.group(1)

    # Match only Unown form rewards (e.g., "Unown-K" or "Shiny Unown-K"), not plain "Unown".
    reward_match = re.search(
        r"reward:?\s+[^\n]*?\*\*((?:Shiny\s+)?Unown-[A-Za-z0-9!?]+)\*\*",
        content,
        re.IGNORECASE,
    )
    if reward_match:
        pokemon_reward = reward_match.group(1)

    return {"username": username, "pokemon_reward": pokemon_reward}


async def process_unown_unlock(bot: discord.Client, message: discord.Message):
    """
    Process a battle result message to check for Unown unlocks and send a webhook notification.

    Args:
        message: The Discord message object containing the battle result.
    """
    extracted_data = extract_from_battle_message(message.content)
    member_name = extracted_data["username"]
    pokemon_reward = extracted_data["pokemon_reward"]

    if not member_name:
        debug_log("Could not extract winner username from battle message content.")
        pretty_log(
            "warning",
            "Unown Unlocks Listener: Could not extract winner username from battle message content.",
        )
        return

    if not pokemon_reward:
        debug_log("Could not extract Pokemon reward from battle message content.")
        pretty_log(
            "warning",
            "Unown Unlocks Listener: Could not extract Pokemon reward from battle message content.",
        )
        return

    # Get member object from the guild using the extracted name
    member = next(
        (
            m
            for m in message.guild.members
            if m.name.lower() == member_name.lower()
            or m.display_name.lower() == member_name.lower()
        ),
        None,
    )
    if member is None:
        debug_log(
            f"No member found matching name '{member_name}' in guild '{message.guild.name}'."
        )
        pretty_log(
            "warning",
            f"Unown Unlocks Listener: No member found matching name '{member_name}' in guild '{message.guild.name}'.",
        )
        return
    rarity = "shiny" if "shiny" in pokemon_reward.lower() else "superrare"
    rarity_info = rarity_meta.get(rarity, rarity_meta["unknown"])
    color = rarity_info["color"]
    display_name = get_display_name(pokemon_reward, dex=True)
    footer_text = "Challenge the Unown ruins using ;b npc 970"
    thumbnail_url = get_pokemon_gif(pokemon_reward)
    description = f"{member.mention} has received {display_name} from defeating the Alph Scientist!"
    title = "Unown Ruins Reward!"

    embed = discord.Embed(
        title=title,
        url=message.jump_url,
        description=description,
        color=color,
        timestamp=datetime.now(),
    )
    embed.set_thumbnail(url=thumbnail_url if thumbnail_url else None)
    embed.set_footer(
        text=footer_text, icon_url=member.guild.icon.url if member.guild.icon else None
    )
    embed.set_author(
        name=member.display_name, icon_url=member.avatar.url if member.avatar else None
    )
    battle_unlocks_channel = get_rarespawn_channel(message.guild)
    if battle_unlocks_channel:
        await send_webhook(
            bot=bot,
            channel=battle_unlocks_channel,
            embed=embed,
        )

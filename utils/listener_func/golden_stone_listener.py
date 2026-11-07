import re

import discord

from utils.functions.webhook_func import send_webhook
from utils.listener_func.res_egg_listener import get_rarespawn_channel
from utils.logs.debug_log import debug_enabled, debug_log, enable_debug
from utils.logs.pretty_log import pretty_log

# enable_debug(f"{__name__}.golden_stone_listener")
BENGA_THUMBNAIL_URL = "https://cdn.discordapp.com/attachments/1382540357123965029/1491214677596962916/chamber_master_benga.png?ex=69d6e164&is=69d58fe4&hm=966ff41faca3ef955a051ba3470f58af02ef1abb648d13d91bd6200bd9d154d1"
IRIA_THUMBNAIL_URL = "https://cdn.discordapp.com/attachments/1382540357123965029/1491214894706593912/chamber_master_iria.png?ex=69d6e198&is=69d59018&hm=a3c27fb484581721c0f0735852247bb104c76c0c0920971ac8fd1276dcc93068"
GAIL_THUMBNAIL_URL = "https://cdn.discordapp.com/attachments/1382540357123965029/1491214995856429056/chamber_master_gail.png?ex=69d6e1b0&is=69d59030&hm=2421806bb3ede373fc95476d5141a78283b674c24a51756df0987d4e294bfd61"
HARMON_THUMBNAIL_URL = "https://cdn.discordapp.com/attachments/1382540357123965029/1491215187561414788/chamber_master_harmon.png?ex=69d6e1de&is=69d5905e&hm=d159452574cda9b7e59db7372e8ccda56ea0c590cdce4a2c6b8e43d6d67444a4"
TESTING = False


# 🌺🧸────────────────────────────────────────────🌺🧸
#       GOLDEN_STONE_HELPERS
# 🌺🧸────────────────────────────────────────────🌺🧸
def get_golden_stone_info(message: str) -> tuple[str, str] | None:
    """
    Extracts the emoji ID of a custom emoji with 'golden_' prefix
    and returns both its Discord CDN URL and the stone name
    (underscores removed, title case).

    Args:
        message (str): The Discord message content.

    Returns:
        tuple[str, str] | None: (emoji_url, stone_name) if found, otherwise None.
    """
    pattern = r"<:golden_([a-zA-Z0-9_]+):(\d+)>"
    match = re.search(pattern, message)
    if match:
        raw_name, emoji_id = match.groups()
        # Format the stone name: remove underscores, title case
        stone_name = raw_name.replace("_", " ").title()
        emoji_url = f"https://cdn.discordapp.com/emojis/{emoji_id}.png"
        return emoji_url, stone_name
    return None


def get_mega_chamber(message: str) -> str | None:
    """
    Extracts the Mega Chamber challenge name (inside **bold**) from a Discord message.

    Args:
        message (str): The Discord message content.

    Returns:
        str | None: The challenge name (e.g. 'Mega Ampharos') if found, otherwise None.
    """
    # Look for bolded text after 'completed the' phrase
    pattern = r"completed the .*?\*\*(.*?)\*\*"
    match = re.search(pattern, message)
    if match:
        return match.group(1)
    return None


def extract_winner_name(content: str) -> str | None:
    """
    Extracts the winner's name from the message content.
    Looks for the pattern: <emote> NAME won the battle
    Returns the name without formatting or emotes.
    """
    # Regex: match anything (optionally with emote and formatting) before "won the battle"
    # Handles bold/italic/underline/strikethrough/monospace formatting
    match = re.search(r"(?:>|\s|^)[*_~`]*([^\n<>*]+?)[*_~`]*\s+won the battle", content)
    if match:
        # Strip leading/trailing whitespace
        return match.group(1).strip()
    return None


async def golden_stone_listener(bot: discord.Client, message: discord.Message):
    """
    Listens for messages indicating a Golden Stone has been obtained
    and logs the event with user details.

    """
    debug_log("Processing message for golden stone claim.")
    member_name = extract_winner_name(message.content)
    if not member_name:
        debug_log("No winner name extracted from message content.")
        pretty_log("info", "Golden Stone Listener: No winner name found in message.")
        debug_log(
            f"Failed to extract winner name from message content: '{message.content}'",
        )
        return
    debug_log(f"Extracted winner name: {member_name}")
    pretty_log("info", f"Golden Stone Listener: Extracted winner name: {member_name}")

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
            f"Golden Stone Listener: No member found matching name '{member_name}' in guild '{message.guild.name}'.",
        )
        return

    result = get_golden_stone_info(message.content)
    if not result:
        debug_log("No golden stone emoji found in message content.")
        return
    emoji_url, stone_name = result
    debug_log(f"Extracted golden stone: {stone_name}, emoji URL: {emoji_url}")

    challenge_name = get_mega_chamber(message.content)
    if not challenge_name:
        debug_log("No Mega Chamber challenge name found in message content.")
        return
    debug_log(f"Extracted Mega Chamber challenge name: {challenge_name}")

    achievements_channel = get_rarespawn_channel(message.guild)
    if not achievements_channel:
        debug_log("Achievements channel not found in guild.")
        return
    embed = message.embeds[0] if message.embeds else None
    embed_title = embed.title if embed else ""
    if "Benga" in embed_title:
        master_url = BENGA_THUMBNAIL_URL
    elif "Iria" in embed_title:
        master_url = IRIA_THUMBNAIL_URL
    elif "Gail" in embed_title:
        master_url = GAIL_THUMBNAIL_URL
    elif "Harmon" in embed_title:
        master_url = HARMON_THUMBNAIL_URL
    else:
        master_url = None

    desc = f"{member.mention} claimed a **Golden {stone_name}** by defeating the **{challenge_name} Golden Finals**!"
    debug_log(f"Composed embed description: {desc}")

    embed = discord.Embed(
        title="🌟 Golden Stone Obtained!",
        url=message.jump_url,
        description=desc,
        color=discord.Color.gold(),
    )
    embed.set_footer(text=f"Defeated in {message.guild.name}", icon_url=emoji_url)
    if master_url:
        embed.set_thumbnail(url=master_url)
    embed.set_author(name=member.display_name, icon_url=member.display_avatar.url)
    if not TESTING:
        debug_log(f"Sending webhook to channel ID: {achievements_channel.id}")
        await send_webhook(
            bot=bot,
            channel=achievements_channel,
            embed=embed,
        )
    else:
        await message.channel.send(embed=embed)
    debug_log("Webhook sent successfully.")

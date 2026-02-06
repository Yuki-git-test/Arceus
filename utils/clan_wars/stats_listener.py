import re
from typing import Optional

import discord

from utils.db.clan_wars_server_members import (
    get_member_clan_name,
    upsert_clan_wars_server_member,
)
from utils.logs.pretty_log import pretty_log
from utils.pokemeow.get_pokemeow_reply import get_pokemeow_reply_member


def extract_clan_name(description: str) -> str:
    """
    Extracts the clan name from a Discord embed description.
    Handles 'Owner of', 'Co-Owner of', 'Member of', and 'None' variants.
    Returns the clan name as a string, or None if not found or 'None'.
    """
    # Find the line containing 'Clan'
    clan_line = None
    for line in description.splitlines():
        if "Clan" in line:
            clan_line = line.strip()
            break
    if not clan_line:
        return None

    # Check for 'None'
    if re.search(r"Clan.*None", clan_line, re.IGNORECASE):
        return None

    # Extract after 'of' (handles emojis and text, including punctuation)
    match = re.search(r"of\s*(?:<a?:\w+:\d+>\s*)?([^\n]+)", clan_line)
    if match:
        return match.group(1).strip()

    # Fallback: try to get last word(s) after colon
    parts = clan_line.split(":")
    if len(parts) > 1:
        possible_name = parts[-1].strip()
        if possible_name and possible_name.lower() != "none":
            return possible_name
    return None


def extract_user_id_from_command(content: str) -> Optional[int]:
    """
    Extracts the user ID from a command snippet like ';stats 123456789012345678'.
    Returns the user ID as an integer if found, else None.
    """
    match = re.search(r";(?:stats|pro|profile)\s+(\d{15,21})", content)
    if match:
        return int(match.group(1))
    return None


async def fetch_member(message: discord.Message) -> Optional[dict]:
    """
    Fetches member object by extracting the userid, falling back to extracting user ID from a replied message's content or member if needed.
    """
    guild = message.guild

    # Fallback: try to get user ID from replied message content
    replied_message = getattr(message.reference, "resolved", None)
    if replied_message:
        replied_message_content = getattr(replied_message, "content", "") or ""
        user_id = extract_user_id_from_command(replied_message_content)
        if user_id:
            # Try to get guild member by ID
            member = guild.get_member(user_id)
            if member:
                return member

        # Fallback: try to get member from replied message
        member = await get_pokemeow_reply_member(message=message)
        if member:
            return member

    return None


async def stats_command_listener(
    bot: discord.Client, before_message: discord.Message, after_message: discord.Message
):
    if not after_message.embeds:
        return

    embed = after_message.embeds[0]
    if not embed.author or not embed.author.name or not embed.description:
        return

    username = embed.author.name.split("'s ")[0]
    embed_description = embed.description

    # Get member obj
    member = await fetch_member(after_message)
    if not member:
        pretty_log(
            "info",
            f"Could not find member for stats command in message ID {after_message.id}",
        )
        return

    clan_name = extract_clan_name(embed_description)
    pretty_log("info", f"Extracted clan name '{clan_name}'")
    # Get old clan name from DB
    old_clan_name = await get_member_clan_name(bot, member.id)
    if clan_name != old_clan_name:
        await upsert_clan_wars_server_member(
            bot,
            user_id=member.id,
            user_name=username,
            clan_name=clan_name,
        )
        pretty_log(
            "info",
            f"Updated clan name for {username} ({member.id}): '{old_clan_name}' -> '{clan_name}'",
        )
        # Add check reaction to the message
        try:
            await after_message.add_reaction("✅")
        except Exception as e:
            pretty_log(
                "error",
                f"Failed to add reaction to message ID {after_message.id}: {e}",
            )

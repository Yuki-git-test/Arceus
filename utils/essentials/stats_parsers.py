import re
import time
from typing import Dict, List, Optional, Tuple

import discord

from utils.logs.pretty_log import pretty_log


async def fetch_message_obj_from_link(
    bot: discord.Client, message_link: str
) -> tuple[Optional[discord.Message], Optional[str]]:
    """Fetches a Discord message object from a given message link."""
    try:
        parts = message_link.strip().split("/")
        guild_id = int(parts[4])
        channel_id = int(parts[5])
        message_id = int(parts[6])
        pretty_log(
            "info",
            f"Parsed message link: guild_id={guild_id}, channel_id={channel_id}, message_id={message_id}",
            label="MSG LINK PARSER",
        )

    except (IndexError, ValueError) as e:
        pretty_log(
            "error", f"Failed to parse message link: {e}", label="MSG LINK PARSER"
        )
        error_message = (
            "Invalid message link format. Please provide a valid Discord message link."
        )
        return None, error_message

    # Fetch the message
    guild = bot.get_guild(guild_id)
    if not guild:
        pretty_log(
            "error", f"Guild with ID {guild_id} not found.", label="MSG LINK PARSER"
        )
        error_message = (
            "Guild not found. Please ensure the bot is in the specified server."
        )
        return None, error_message
    channel = guild.get_channel(channel_id)
    if not channel:
        pretty_log(
            "error",
            f"Channel with ID {channel_id} not found in guild {guild_id}.",
            label="MSG LINK PARSER",
        )
        error_message = "Channel not found. Please ensure the channel exists in the specified server."
        return None, error_message

    try:
        message = await channel.fetch_message(message_id)
        pretty_log(
            "info",
            f"Successfully fetched message ID {message_id} from channel ID {channel_id}.",
            label="MSG LINK PARSER",
        )
        return message, None
    except discord.NotFound:
        pretty_log(
            "error",
            f"Message with ID {message_id} not found in channel {channel_id}.",
            label="MSG LINK PARSER",
        )
        error_message = "Message not found. Please ensure the message ID is correct."
        return None, error_message


def calculate_total_catches(catches: int, fishes: int) -> int:
    total_catches = catches + fishes
    return total_catches


def format_display_amount(amount: int) -> str:
    """
    Converts integer to a string with commas:
        30000 -> '30,000'
    """
    return f"{amount:,}"


def shorten_amount(amount: int) -> str:
    """
    Converts an integer into a compact short format:
        30000 -> '30k', 1500000 -> '1.5m'
    """
    if amount >= 1_000_000:
        return f"{amount / 1_000_000:.1f}m".rstrip("0").rstrip(".")
    elif amount >= 1_000:
        return f"{amount / 1_000:.1f}k".rstrip("0").rstrip(".")
    return str(amount)


def trim_header(message: str) -> str:
    """
    Removes header lines like timestamps, totals, and "You're Rank" before the first actual member line.
    Returns the trimmed message starting from the first detected user entry line.
    """
    lines = message.splitlines()
    start_idx = 0

    for i, line in enumerate(lines):
        line = line.strip()
        # Detect rank line e.g. **1** username
        if re.match(r"\*\*\d+\*\*\s+.+", line):
            start_idx = i
            break
        # Or detect a non-empty line not starting with known emojis or rank header
        if (
            line
            and not line.startswith(":dexcaught:")
            and not line.startswith("<:dexcaught:")
            and not line.startswith("You're Rank")
            and not line.startswith(":calendar:")
            and not line.startswith(":bar_chart:")
        ):
            start_idx = i
            break  # <-- Added break here to stop after first valid line found

    return "\n".join(lines[start_idx:])


def should_parse(embed_title: Optional[str]) -> bool:
    """
    Checks if the embed title contains the required substring to consider parsing.
    Accepts both weekly and monthly clan stats titles.
    """
    if not embed_title:
        return False
    return (
        "Clan Weekly Stats — Straymons" in embed_title
        or "Clan Monthly Stats — Straymons" in embed_title
    )


def clean_username(username: str) -> str:
    # Strip any leading/trailing ** from username cleanly
    return re.sub(r"^\*+|\*+$", "", username).strip()


def parse_clan_stats_message(message: str) -> Optional[List[Tuple[str, int, int]]]:
    message = trim_header(message)
    lines = message.splitlines()

    members = []

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # Make detection smarter: skip any line containing "You're Rank"
        if "You're Rank" in line:
            i += 1
            continue

        rank_match = re.match(r"\*\*(\d+)\*\*\s+(.+)", line)
        if rank_match:
            rank_number = int(rank_match.group(1))
            username = clean_username(rank_match.group(2))
            # You can now use rank_number as needed, e.g. store it with the member tuple
            i += 1
        elif not line.startswith(":dexcaught:") and not line.startswith("<:dexcaught:"):
            username = clean_username(line)
            i += 1
        else:
            i += 1
            continue

        if i < len(lines):
            stats_line = lines[i].strip()

            catch_match = re.search(
                r"(?:<:dexcaught:\d+>|:dexcaught:)\s*([\d,]+)", stats_line
            )
            fish_match = re.search(r"(?:<:oldrod:\d+>|:oldrod:)\s*([\d,]+)", stats_line)

            catches = int(catch_match.group(1).replace(",", "")) if catch_match else 0
            fishes = int(fish_match.group(1).replace(",", "")) if fish_match else 0

            members.append((username, catches, fishes))

        i += 1
    return members


def print_clean_stats(members: List[Tuple[str, int, int]]) -> None:
    """
    Helper function to print stats cleanly without emojis,
    formatting large numbers in compact + readable forms.
    """
    for username, catches, fishes in members:
        total = calculate_total_catches(catches, fishes)

        # Format each number as "30,000 (30k)" style
        catches_display = format_display_amount(catches)
        catches_short = shorten_amount(catches)
        fishes_display = format_display_amount(fishes)
        fishes_short = shorten_amount(fishes)
        total_display = format_display_amount(total)
        total_short = shorten_amount(total)

        pretty_log(
            "info",
            f"Username: {username} | Catches: {catches_display} ({catches_short}) | "
            f"Fishes: {fishes_display} ({fishes_short}) | "
            f"Total: {total_display} ({total_short})",
            label="CLAN STATS PARSER",
        )


def parse_clan_stats_message_with_rank_number(
    message: str,
) -> Optional[List[Tuple[int, str, int, int]]]:
    message = trim_header(message)
    lines = message.splitlines()

    members = []

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # Make detection smarter: skip any line containing "You're Rank"
        if "You're Rank" in line:
            i += 1
            continue

        rank_match = re.match(r"\*\*(\d+)\*\*\s+(.+)", line)
        if rank_match:
            rank_number = int(rank_match.group(1))
            username = clean_username(rank_match.group(2))
            # You can now use rank_number as needed, e.g. store it with the member tuple
            i += 1
        elif not line.startswith(":dexcaught:") and not line.startswith("<:dexcaught:"):
            username = clean_username(line)
            i += 1
        else:
            i += 1
            continue

        if i < len(lines):
            stats_line = lines[i].strip()

            catch_match = re.search(
                r"(?:<:dexcaught:\d+>|:dexcaught:)\s*([\d,]+)", stats_line
            )
            fish_match = re.search(r"(?:<:oldrod:\d+>|:oldrod:)\s*([\d,]+)", stats_line)

            catches = int(catch_match.group(1).replace(",", "")) if catch_match else 0
            fishes = int(fish_match.group(1).replace(",", "")) if fish_match else 0

            members.append((rank_number, username, catches, fishes))

        i += 1

    return members


async def split_known_and_unknown_members(
    bot: discord.Client,
    members: List[Tuple[str, int, int]],  # (username, catches, fishes)
    guild: discord.Guild,
) -> Tuple[
    List[Tuple[discord.Member, str, int, int]],  # known
    List[Tuple[str, int, int]],  # unknown
]:
    """
    Splits members into known/unknown by matching usernames against
    user_ids stored in infusion members cache.

    - Only considers guild members whose IDs exist in the DB.
    - Lookup is done against both display_name and username.
    """

    known: List[Tuple[discord.Member, str, int, int]] = []
    unknown: List[Tuple[str, int, int]] = []

    # Step 1: Grab all user_ids registered in cache
    from utils.cache.vna_members_cache import fetch_all_user_ids_from_cache

    user_ids = fetch_all_user_ids_from_cache()

    # Step 2: Build a lookup dict for fast matching
    name_lookup: Dict[str, discord.Member] = {}
    for uid in user_ids:
        member = guild.get_member(uid)
        if member:
            name_lookup[member.name.lower()] = member
            name_lookup[member.display_name.lower()] = member

    # Step 3: Match parsed usernames directly
    for username, catches, fishes in members:
        match = name_lookup.get(username.lower())
        if match:
            known.append((match, username, catches, fishes))
        else:
            # try to match the pokemeow name from cache
            from utils.cache.vna_members_cache import (
                fetch_vna_member_id_by_pokemeow_name,
            )

            user_id = fetch_vna_member_id_by_pokemeow_name(username)
            if user_id:
                member = guild.get_member(user_id)
                if member:
                    known.append((member, username, catches, fishes))
                    continue
                else:
                    unknown.append((username, catches, fishes))
            else:
                unknown.append((username, catches, fishes))

    return known, unknown

import re

import discord

from Constants.vn_allstars_constants import (
    MONTHLY_REQUIREMENT,
    VN_ALLSTARS_ROLES,
    VN_ALLSTARS_TEXT_CHANNELS,
    WEEKLY_REQUIREMENT,
)
from utils.cache.cache_list import processed_explore_messages, vna_members_cache
from utils.db.monthly_goal_tracker import upsert_monthly_goal
from utils.db.weekly_goal_tracker import upsert_weekly_goal
from utils.logs.pretty_log import pretty_log
from utils.pokemeow.get_pokemeow_reply import get_pokemeow_reply_member

from .pokemon_caught_listener import goal_checker


async def explore_caught_listener(
    bot: discord.Client, before_message: discord.Message, after_message: discord.Message
):
    """Listener function to track processed explore messages."""

    if after_message.id in processed_explore_messages:
        return
    processed_explore_messages.add(after_message.id)

    # Get member info
    member: discord.Member = get_pokemeow_reply_member(before_message)
    if not member:
        return

    member_id = member.id
    member_name = member.name
    guild = after_message.guild

    # Check if member has the VN Allstars role
    vna_member_role = guild.get_role(VN_ALLSTARS_ROLES.vna_member)
    if vna_member_role not in member.roles:
        return

    vna_member_info = vna_members_cache.get(member_id)
    if not vna_member_info:
        return
    personal_channel_id = vna_member_info.get("channel_id") if vna_member_info else None

    # Add to Weekly and Monthly Goal Caches if not in cache
    from utils.cache.cache_list import monthly_goal_cache, weekly_goal_cache
    from utils.cache.monthly_goal_tracker_cache import (
        mark_monthly_goal_dirty,
        set_monthly_pokemon_caught,
    )
    from utils.cache.weekly_goal_tracker_cache import (
        mark_weekly_goal_dirty,
        set_pokemon_caught,
    )

    if member_id not in weekly_goal_cache:
        await upsert_weekly_goal(
            bot,
            user_id=member_id,
            user_name=member_name,
            channel_id=personal_channel_id,
            pokemon_caught=0,
            fish_caught=0,
            battles_won=0,
            weekly_requirement_mark=False,
        )
    if member_id not in monthly_goal_cache:
        await upsert_monthly_goal(
            bot,
            user_id=member_id,
            user_name=member_name,
            channel_id=personal_channel_id,
            pokemon_caught=0,
            fish_caught=0,
            battles_won=0,
            monthly_requirement_mark=False,
        )

    content = after_message.content or ""
    if not content:
        return

    # Extract number of Pokemon caught from the message content
    match = re.search(r"Pokémon caught \((\d+)\):", content)
    if not match:
        return

    caught_count = int(match.group(1))
    pretty_log(
        "info",
        f"🟢 Explore caught listener: Member {member_name} ({member_id}) has caught {caught_count} Pokémon.",
    )

    # Get current weekly and monthly caught counts
    current_weekly_caught = weekly_goal_cache[member_id].get("pokemon_caught", 0)
    current_monthly_caught = monthly_goal_cache[member_id].get("pokemon_caught", 0)

    # Update caches with new caught counts
    new_weekly_caught = current_weekly_caught + caught_count
    set_pokemon_caught(member, new_weekly_caught)
    mark_weekly_goal_dirty(member_id)
    new_monthly_caught = current_monthly_caught + caught_count
    set_monthly_pokemon_caught(member, new_monthly_caught)
    mark_monthly_goal_dirty(member_id)

    pretty_log(
        "info",
        f"Updated {member_name}'s caught counts: Weekly={new_weekly_caught}, Monthly={new_monthly_caught}",
    )
    # Check for goal completion
    await goal_checker(
        bot=bot,
        user_id=member_id,
        user_name=member_name,
        guild=guild,
        channel=after_message.channel,
    )
    pretty_log(
        "info",
        f"✅ Explore caught listener processing complete for Member {member_name} ({member_id}).",
    )

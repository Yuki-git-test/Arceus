import re

import discord

from Constants.vn_allstars_constants import (
    MONTHLY_REQUIREMENT,
    VN_ALLSTARS_ROLES,
    VN_ALLSTARS_TEXT_CHANNELS,
    WEEKLY_REQUIREMENT,
)
from utils.cache.cache_list import processed_monthly_stats_messages, vna_members_cache
from utils.db.monthly_goal_tracker import fetch_all_monthly_goals, upsert_monthly_goal
from utils.db.weekly_goal_tracker import fetch_all_weekly_goals, upsert_weekly_goal
from utils.essentials.stats_parsers import (
    parse_clan_stats_message,
    split_known_and_unknown_members,
)
from utils.logs.pretty_log import pretty_log
from utils.pokemeow.get_pokemeow_reply import (
    get_message_interaction_member,
    get_pokemeow_reply_member,
)

from .pokemon_caught_listener import goal_checker
from .weekly_stats_listener import extract_current_page_number


async def monthly_stats_listener(
    bot: discord.Client, before_message: discord.Message, after_message: discord.Message
):
    embed = after_message.embeds[0] if after_message.embeds else None
    if not embed:
        return
    embed_footer = embed.footer.text
    embed_description = embed.description or ""

    # Get command user
    command_user: discord.Member = await get_pokemeow_reply_member(before_message)
    if not command_user:
        # Fallback to interaction user
        command_user = get_message_interaction_member(before_message)
        if not command_user:
            return

    command_user_id = command_user.id
    command_user_name = command_user.name
    guild = after_message.guild

    # Extract current page number
    current_page = extract_current_page_number(embed_footer)
    # Check if current page and message id is in processed messages
    key = (after_message.id, current_page)
    if key in processed_monthly_stats_messages:
        return
    processed_monthly_stats_messages.add(key)

    # Check if command user is in monthly and weekly goal caches
    from utils.cache.cache_list import (
        monthly_goal_cache,
        vna_members_cache,
        weekly_goal_cache,
    )

    vna_member_info = vna_members_cache.get(command_user_id)
    personal_channel_id = vna_member_info.get("channel_id") if vna_member_info else None
    if command_user_id not in weekly_goal_cache:

        await upsert_weekly_goal(
            bot=bot,
            user_id=command_user_id,
            user_name=command_user_name,
            channel_id=personal_channel_id,
            pokemon_caught=0,
            fish_caught=0,
            battles_won=0,
            weekly_requirement_mark=False,
        )
    if command_user_id not in monthly_goal_cache:
        await upsert_monthly_goal(
            bot=bot,
            user_id=command_user_id,
            user_name=command_user_name,
            channel_id=personal_channel_id,
            pokemon_caught=0,
            fish_caught=0,
            battles_won=0,
            monthly_requirement_mark=False,
        )

    top_line_catches = 0
    # Get top line catches
    user_top_line_match = re.search(
        r"You're Rank \d+ in your clan's monthly stats — with ([\d,]+) catches!",
        embed_description,
    )
    top_line_catches = 0
    if user_top_line_match:
        top_line_catches = int(user_top_line_match.group(1).replace(",", ""))
        pretty_log(
            "info",
            f"Top line catches for {command_user_name}: {top_line_catches}",
            label="💠 MONTHLY STATS DEBUG",
            bot=bot,
        )
        # Goal checking
        if top_line_catches >= MONTHLY_REQUIREMENT and current_page == 1:
            await goal_checker(
                bot=bot,
                user_id=command_user_id,
                user_name=command_user_name,
                channel=after_message.channel,
                top_line_monthly_catches=top_line_catches,
                context="stats_command",
                guild=guild,
            )
            pretty_log(
                "info",
                f"Monthly stats listener: User {command_user_name} ({command_user_id}) has {top_line_catches} weekly catches.",
            )

    # Parse clan members stats
    clan_members_stats = parse_clan_stats_message(embed_description)
    if not clan_members_stats:
        return

    # Fetch old weekly goals from DB
    from utils.cache.vna_members_cache import (
        fetch_vna_member_id_by_username_or_pokemeow_name,
    )

    old_monthly_goals = await fetch_all_monthly_goals(bot=bot)
    # Convert list of dicts to dict keyed by user_id for fast lookup
    old_monthly_goals_dict = {g["user_id"]: g for g in old_monthly_goals}
    if not old_monthly_goals:
        # Upsert all members as new if no old goals found
        for username, catches, fishes in clan_members_stats:
            member_id = fetch_vna_member_id_by_username_or_pokemeow_name(username)
            member_info = vna_members_cache.get(member_id) if member_id else None
            channel_id = member_info.get("channel_id") if member_info else None
            if username == "neverlikenever_42984":
                member_id = 1327864338018730044  # Manually set member ID for this user
                
            await upsert_monthly_goal(
                bot=bot,
                user_id=member_id,
                user_name=username,
                channel_id=channel_id,
                pokemon_caught=catches,
                fish_caught=fishes,
                battles_won=0,
                monthly_requirement_mark=False,
            )
            await goal_checker(
                bot=bot,
                user_id=member_id,
                user_name=username,
                channel=after_message.channel,
                context="stats_command",
                guild=guild,
            )
    else:
        # Compare values
        for username, catches, fishes in clan_members_stats:
            member_id = fetch_vna_member_id_by_username_or_pokemeow_name(username)
            # Compare from old weekly goals from db
            old_goal = old_monthly_goals_dict.get(member_id)
            old_catches = old_goal.get("pokemon_caught") if old_goal else 0
            old_fishes = old_goal.get("fish_caught") if old_goal else 0
            if catches != old_catches or fishes != old_fishes:
                member_info = vna_members_cache.get(member_id) if member_id else None
                channel_id = member_info.get("channel_id") if member_info else None
                await upsert_monthly_goal(
                    bot=bot,
                    user_id=member_id,
                    user_name=username,
                    channel_id=channel_id,
                    pokemon_caught=catches,
                    fish_caught=fishes,
                    battles_won=0,
                    monthly_requirement_mark=False,
                )
                await goal_checker(
                    bot=bot,
                    user_id=member_id,
                    user_name=username,
                    channel=after_message.channel,
                    context="stats_command",
                    guild=guild,
                )

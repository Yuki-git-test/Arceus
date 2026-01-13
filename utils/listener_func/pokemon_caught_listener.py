import re

import discord

from Constants.vn_allstars_constants import (
    ARCEUS_EMBED_COLOR,
    MONTHLY_REQUIREMENT,
    VN_ALLSTARS_TEXT_CHANNELS,
    WEEKLY_REQUIREMENT,
)
from utils.cache.cache_list import processed_caught_messages
from utils.db.monthly_goal_tracker import upsert_monthly_goal
from utils.db.weekly_goal_tracker import upsert_weekly_goal
from utils.functions.webhook_func import send_webhook
from utils.logs.debug_log import debug_log, enable_debug
from utils.logs.pretty_log import pretty_log
from utils.pokemeow.get_pokemeow_reply import get_pokemeow_reply_member

#enable_debug(f"{__name__}.goal_checker")
# enable_debug(f"{__name__}.pokemon_caught_listener")
FISHING_COLOR = 0x87CEFA


async def goal_checker(
    bot: discord.Client,
    user_id: int,
    user_name: str,
    guild: discord.Guild,
    channel: discord.TextChannel,
    top_line_weekly_catches: int = None,
    top_line_monthly_catches: int = None,
    context: str = None,
):
    # return  # Temporarily disable goal checking
    from utils.cache.cache_list import monthly_goal_cache, weekly_goal_cache
    from utils.cache.monthly_goal_tracker_cache import update_monthly_requirement_mark
    from utils.cache.weekly_goal_tracker_cache import update_weekly_requirement_mark

    # Get current caught counts
    weekly_pokemon_caught = weekly_goal_cache.get(user_id, {}).get("pokemon_caught", 0)
    monthly_pokemon_caught = monthly_goal_cache.get(user_id, {}).get(
        "pokemon_caught", 0
    )
    weekly_fish_caught = weekly_goal_cache.get(user_id, {}).get("fish_caught", 0)
    monthly_fish_caught = monthly_goal_cache.get(user_id, {}).get("fish_caught", 0)
    weekly_requirement_mark = weekly_goal_cache.get(user_id, {}).get(
        "weekly_requirement_mark", False
    )
    monthly_requirement_mark = monthly_goal_cache.get(user_id, {}).get(
        "monthly_requirement_mark", False
    )

    # Compute total
    total_weekly_caught = weekly_pokemon_caught + weekly_fish_caught
    total_monthly_caught = monthly_pokemon_caught + monthly_fish_caught

    debug_log(
        f"total_weekly_caught={total_weekly_caught}, total_monthly_caught={total_monthly_caught}"
    )
    goal_tracker_channel = guild.get_channel(VN_ALLSTARS_TEXT_CHANNELS.goal_tracker)
    # Update weekly requirement mark
    if not weekly_requirement_mark:
        if (
            weekly_pokemon_caught >= WEEKLY_REQUIREMENT
            or total_weekly_caught >= WEEKLY_REQUIREMENT
            or weekly_fish_caught >= WEEKLY_REQUIREMENT
        ) or (
            top_line_weekly_catches and top_line_weekly_catches >= WEEKLY_REQUIREMENT
        ):

            update_weekly_requirement_mark(user_id, True)
            pretty_log(f"User {user_name} has met the weekly requirement.")
            if not context or context != "stats_command":
                await channel.send(
                    f"🎉 Congratulations {user_name}! You have met the weekly requirement of {WEEKLY_REQUIREMENT:,}"
                )
            if goal_tracker_channel:
                user = guild.get_member(user_id)

                if not user:
                    # Fetch user via user id
                    user = await bot.fetch_user(user_id)
                user_line = user.mention if user else user_name
                avatar_url = user.display_avatar.url if user else None
                embed = discord.Embed(
                    description=f"🎉 {user_line} has met the weekly requirement of __{WEEKLY_REQUIREMENT:,}__ catches!",
                    color=ARCEUS_EMBED_COLOR,
                )
                embed.set_author(name=user.display_name, icon_url=avatar_url)
                await send_webhook(
                    bot=bot,
                    channel=goal_tracker_channel,
                    embed=embed,
                )

    if not monthly_requirement_mark:
        if (
            monthly_pokemon_caught >= MONTHLY_REQUIREMENT
            or total_monthly_caught >= MONTHLY_REQUIREMENT
            or monthly_fish_caught >= MONTHLY_REQUIREMENT
        ) or (
            top_line_monthly_catches and top_line_monthly_catches >= MONTHLY_REQUIREMENT
        ):
            update_monthly_requirement_mark(user_id, True)
            pretty_log(f"User {user_name} has met the monthly requirement.")
            if not context or context != "stats_command":
                await channel.send(
                    f"🏆 Congratulations {user_name}! You have met the monthly requirement of {MONTHLY_REQUIREMENT:,}"
                )
            if goal_tracker_channel:
                user = guild.get_member(user_id)

                if not user:
                    # Fetch user via user id
                    user = await bot.fetch_user(user_id)

                avatar_url = user.display_avatar.url if user else None
                user_line = user.mention if user else user_name
                embed = discord.Embed(
                    description=f"🏆 {user_line} has met the monthly requirement of __{MONTHLY_REQUIREMENT:,}__ catches!",
                    color=0xFFD700,
                )
                embed.set_author(name=user.display_name, icon_url=avatar_url)
                await send_webhook(
                    bot=bot,
                    channel=goal_tracker_channel,
                    embed=embed,
                )


def extract_member_username_from_embed(embed: discord.Embed) -> str | None:
    """
    Extracts the username from the embed author name, e.g. "Congratulations, frayl!" -> "frayl".
    Returns None if not found.
    """
    if embed.author and embed.author.name:
        # Try 'Congratulations, username!' first
        match = re.search(r"Congratulations, ([^!]+)!", embed.author.name)
        if match:
            return match.group(1).strip()
        # Fallback: 'Well done, username!'
        match = re.search(r"Well done, ([^!]+)!", embed.author.name)
        if match:
            return match.group(1).strip()
        # Fallback: 'Great work, username!'
        match = re.search(r"Great work, ([^!]+)!", embed.author.name)
        if match:
            return match.group(1).strip()
    return None


# Pokemon Caught Listener
async def pokemon_caught_listener(
    bot: discord.Client,
    before_message: discord.Message,
    after_message: discord.Message,
):
    from utils.cache.vna_members_cache import (
        fetch_vna_member_id_by_username_or_pokemeow_name,
        vna_members_cache,
    )

    if not after_message.embeds:
        debug_log("No embeds found in after_message.")
        return
    embed = after_message.embeds[0]

    member = await get_pokemeow_reply_member(before_message)
    debug_log(f"Pokémon caught listener - initial member: {member}")
    if not member:
        # Try to extract username from embed author
        username = extract_member_username_from_embed(embed)
        debug_log(f"Extracted username from embed: {username}")
        if not username:
            pretty_log(
                "info",
                "⚠️ Could not determine user from Pokémon caught message embed.",
            )
            return
        user_id = fetch_vna_member_id_by_username_or_pokemeow_name(username)
        debug_log(f"Fetched user_id from username: {user_id}")
        if not user_id:
            pretty_log(
                "info",
                f"⚠️ Could not find VNA member for username '{username}' from Pokémon caught message embed.",
            )
            return
        member = after_message.guild.get_member(user_id)
        debug_log(f"Fetched member from guild: {member}")
        if not member:
            pretty_log(
                "info",
                f"⚠️ Could not find Discord member for VNA member ID '{user_id}' from Pokémon caught message embed.",
            )
            return

    member_id = member.id
    member_name = member.name
    debug_log(f"member_id={member_id}, member_name={member_name}")

    # Add member to Weekly Goal Tracker and Monthly Goal Tracker caches if not present
    from utils.cache.cache_list import (
        monthly_goal_cache,
        vna_members_cache,
        weekly_goal_cache,
    )
    from utils.cache.monthly_goal_tracker_cache import (
        increment_monthly_fish_caught,
        mark_monthly_goal_dirty,
        set_monthly_pokemon_caught,
        upsert_monthly_goal_cache,
    )
    from utils.cache.weekly_goal_tracker_cache import (
        increment_fish_caught,
        mark_weekly_goal_dirty,
        set_pokemon_caught,
        upsert_weekly_goal_cache,
    )

    vna_member_info = vna_members_cache.get(member_id)
    debug_log(f"vna_member_info={vna_member_info}")
    if not vna_member_info:
        pretty_log(
            "info",
            f"⚠️ VNA member info not found in cache for member ID {member_id} ({member_name}).",
        )
        return

    personal_channel_id = vna_member_info.get("channel_id") if vna_member_info else None
    debug_log(f"personal_channel_id={personal_channel_id}")

    if member_id not in weekly_goal_cache:
        debug_log(f"member_id {member_id} not in weekly_goal_cache, upserting...")
        try:
            await upsert_weekly_goal(
                bot,
                member_id,
                member_name,
                personal_channel_id,
                pokemon_caught=0,
                fish_caught=0,
                battles_won=0,
                weekly_requirement_mark=False,
            )
            pretty_log(
                "info",
                f"Upserted weekly goal for member ID {member_id} ({member_name}).",
            )
        except Exception as e:
            pretty_log(
                "error",
                f"❌ Exception while upserting weekly goal for member ID {member_id}: {e}",
            )
            return

    if member_id not in monthly_goal_cache:
        debug_log(f"member_id {member_id} not in monthly_goal_cache, upserting...")
        await upsert_monthly_goal(
            bot,
            member_id,
            member_name,
            personal_channel_id,
            pokemon_caught=0,
            fish_caught=0,
            battles_won=0,
            monthly_requirement_mark=False,
        )

    embed_color = embed.color.value if embed.color else None
    embed_description = embed.description or ""
    debug_log(f"embed_color={embed_color}, embed_description={embed_description}")

    # Prevent double processing
    if after_message.id in processed_caught_messages:
        debug_log(f"after_message.id {after_message.id} already processed.")
        return
    processed_caught_messages.add(after_message.id)

    # Fish catch
    if embed_color == FISHING_COLOR:
        debug_log(f"Detected fish catch for member_id {member_id}")
        increment_fish_caught(member)
        increment_monthly_fish_caught(member)
        mark_monthly_goal_dirty(member_id)
        mark_weekly_goal_dirty(member_id)

    else:
        current_weekly_caught = weekly_goal_cache[member_id].get("pokemon_caught", 0)
        current_monthly_caught = monthly_goal_cache[member_id].get("pokemon_caught", 0)
        new_weekly_caught = current_weekly_caught + 1
        new_monthly_caught = current_monthly_caught + 1
        debug_log(
            f"Incrementing caught counts: weekly {new_weekly_caught}, monthly {new_monthly_caught}"
        )
        set_pokemon_caught(member, new_weekly_caught)
        set_monthly_pokemon_caught(member, new_monthly_caught)
        mark_weekly_goal_dirty(member_id)
        mark_monthly_goal_dirty(member_id)

    # Check for goal completion
    await goal_checker(
        bot=bot,
        user_id=member_id,
        user_name=member_name,
        guild=after_message.guild,
        channel=after_message.channel,
    )

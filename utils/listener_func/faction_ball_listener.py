import re

import discord

from Constants.faction_data import FACTION_LOGO_EMOJIS, get_faction_by_emoji
from utils.cache.cache_list import daily_faction_ball_cache, faction_members_cache
from utils.db.daily_faction_ball import update_faction_ball
from utils.db.faction_members import update_faction_member_faction
from utils.logs.pretty_log import pretty_log
from utils.pokemeow.get_pokemeow_reply import get_pokemeow_reply_member
from Constants.vn_allstars_constants import VN_ALLSTARS_ROLES

# 🛡️────────────────────────────────────────────
#      🛡️ Extract Faction Ball from Faction Command
# 🛡️────────────────────────────────────────────
async def extract_faction_ball_from_fa(bot, message: discord.Message):
    # Extract faction from author line (e.g. "Team Magma — Headquarters")
    embed = message.embeds[0] if message.embeds else None
    if not embed:
        return

    faction = None
    if not embed.author or not embed.author.name:
        return

    author_name = embed.author.name
    faction_match = re.search(r"Team (\w+)", author_name)
    if not faction_match:
        return

    faction = faction_match.group(1).lower()

    # Check if there is already a ball for that faction
    daily_ball_faction = daily_faction_ball_cache.get(faction)

    # Extract ball from embed description (e.g. "Your faction's daily ball-type is <:ball_emoji:ID> BallName")
    daily_ball = None
    if not embed.description:
        return

    ball_match = re.search(
        r"<:([a-zA-Z0-9_]+):\d+>\s+\*\*Today's target Pokemon are\*\*",
        embed.description,
    )
    if not ball_match:
        return

    daily_ball = ball_match.group(1)

    # Update db and cache
    if daily_ball and not daily_ball_faction:
        await update_faction_ball(bot, faction, daily_ball)

    member = await get_pokemeow_reply_member(message)
    if not member:
        return

    # Check if member is in faction members cache
    user_id = member.id
    faction_member = faction_members_cache.get(user_id)
    if not faction_member:
        return

    # Update faction if different
    faction_member_info = faction_members_cache.get(user_id)
    if faction_member_info:
        current_faction = faction_member_info.get("faction")
        if current_faction != faction:
            await update_faction_member_faction(bot, user_id, faction)

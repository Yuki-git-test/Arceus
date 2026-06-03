# 🟣────────────────────────────────────────────
#           💜 EV Tracker Brain: Track 💜
# 🟣────────────────────────────────────────────
from datetime import datetime

import discord

from Constants.aesthetic import *
from Constants.vn_allstars_constants import VN_ALLSTARS_TEXT_CHANNELS, DEFAULT_EMBED_COLOR
from utils.cache.cache_list import ev_tracker_cache
from utils.db.ev_tracker_db import add_or_update_ev
from utils.db.market_value_db import fetch_emoji_id_db
from utils.functions.pokemon_func import get_dex_number_by_name, get_display_name
from utils.functions.webhook_func import send_webhook
from utils.logs.debug_log import debug_log, enable_debug
from utils.logs.pretty_log import pretty_log
from utils.visuals.design_embed import design_embed
from utils.visuals.pretty_defer import pretty_defer

STAFF_LOG_CHANNEL_ID = VN_ALLSTARS_TEXT_CHANNELS.server_log

MAX_EVS_PER_STAT = 252
MAX_TOTAL_EVS = 510

# 🟣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#   💜 Rotom Helper Function › Build EV Lines 💜
# 🟣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


def build_ev_lines(evs_to_track: dict, goals_to_track: dict) -> list[str]:
    """Builds formatted EV lines for a Pokemon."""
    lines = []
    for stat, current in evs_to_track.items():
        goal = goals_to_track.get(stat)
        if goal is not None:
            lines.append(f"- {stat.upper()}: {current}/{goal}")
        else:
            lines.append(f"- {stat.upper()}: {current}")
    return lines


# 🤍━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#   ✨ Rotom Core Function › EV Tracker Add ✨
# 🤍━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
async def ev_tracker_add_func(
    bot,
    interaction: discord.Interaction,
    pokemon: str,
    hp=None,
    atk=None,
    spa=None,
    def_=None,
    spd=None,
    spe=None,
):

    emoji_id = None
    user = interaction.user
    user_id = user.id

    # 💜 Start loader
    handle = await pretty_defer(
        interaction, content="Tracking your EVs...", ephemeral=False
    )

    # ✨──────── Step 1 › Collect EV stats with goals ─────✨
    evs_to_track = {}
    goals_to_track = {}
    total_goal_sum = 0

    for stat, val in (
        ("hp", hp),
        ("atk", atk),
        ("spa", spa),
        ("def", def_),
        ("spd", spd),
        ("spe", spe),
    ):
        if val is not None:
            val_str = str(val).strip()

            if "/" not in val_str:
                await handle.error(
                    content=f"Invalid format for **{stat.upper()}**. Use `current/goal` (e.g., 0/252)."
                )
                return

            parts = val_str.split("/")
            try:
                current = int(parts[0].strip())
                goal = int(parts[1].strip()) if len(parts) > 1 else None
            except ValueError:
                await handle.error(
                    content=f"Invalid number for **{stat.upper()}**. Use integers only (e.g., 0/252)."
                )
                return

            if goal is not None and goal > MAX_EVS_PER_STAT:
                await handle.error(
                    content=f"The goal for **{stat.upper()}** cannot exceed {MAX_EVS_PER_STAT}."
                )
                return

            evs_to_track[stat] = current
            if goal is not None:
                goals_to_track[stat] = goal
                total_goal_sum += goal

    if not evs_to_track:
        await handle.error(content="You must provide at least one EV to track.")
        return

    if total_goal_sum > MAX_TOTAL_EVS:
        await handle.error(
            content=f"The total sum of your EV goals ({total_goal_sum}) exceeds {MAX_TOTAL_EVS}."
        )
        return

    # ✨──────── Step 2 › Resolve Pokemon ─────✨
    from utils.db.market_value_db import check_pokemon_in_cache, fetch_emoji_id_cache

    check_pokemon_in_cache(pokemon)
    if not check_pokemon_in_cache(pokemon):
        await handle.error(
            content=f"Pokémon '{pokemon}' not found. Please check the name and try again."
        )
        return

    pokemon_title = pokemon.title()
    dex_number = get_dex_number_by_name(pokemon_title)

    # Fetch emoji ID from cache

    emoji_id = fetch_emoji_id_cache(pokemon_title)
    if not emoji_id:
        # Fetch from DB as fallback
        emoji_id = await fetch_emoji_id_db(bot, pokemon_title)

    has_emoji = False if emoji_id is None else True

    # ✨──────── Step 3 › Save to Database ─────✨
    try:
        await add_or_update_ev(
            bot,
            user_id,
            user.name,
            pokemon_title,
            evs_to_track,
            goals=goals_to_track,
            dex_number=dex_number,
            emoji_id=emoji_id,
        )

        # 💜 Insert/update cache instead of full reload
        from utils.cache.ev_tracker_cache import insert_ev_tracker_cache

        insert_ev_tracker_cache(
            {
                "user_id": user_id,
                "user_name": user.name,
                "pokemon": pokemon_title,
                "emoji_id": emoji_id,
                "dex_number": dex_number,
                "emoji_id": emoji_id,
                **evs_to_track,
                **{f"{k}_goal": v for k, v in goals_to_track.items()},
            }
        )

        # ✨──────── Step 4 › Build Confirmation Embed ─────✨
        display_formatted_name = get_display_name(pokemon_title, dex=dex_number)
        user_desc_lines = [f"- **Pokemon:** {display_formatted_name}\n**EVs:**"]
        user_desc_lines.extend(build_ev_lines(evs_to_track, goals_to_track))

        embed = discord.Embed(
            title=f"EV Tracker Started",
            description="\n".join(user_desc_lines),
            color=DEFAULT_EMBED_COLOR,
        )

        embed = design_embed(embed=embed, user=user, pokemon_name=pokemon_title)
        content = (
            None
            if has_emoji
            else f"Kindly do `;m view {dex_number}` to let me know your Pokémon's dex emoji for tracking EVs!"
        )
        await handle.success(
            embed=embed,
            content=content,
        )

        pretty_log(
            tag="sent",
            message=f"User {user.name} started tracking {pokemon_title} EVs: {evs_to_track} with goals {goals_to_track}",
        )
        formatted_name = get_display_name(pokemon_title, dex=True)

        # ✨──────── Step 5 › Send Staff Log Embed ─────✨
        staff_channel = bot.get_channel(STAFF_LOG_CHANNEL_ID)
        if staff_channel:
            staff_desc_lines = [
                f"- **Member:** {user.mention}\n- **Pokemon:** {display_formatted_name}\n**EVs:**"
            ]
            staff_desc_lines.extend(build_ev_lines(evs_to_track, goals_to_track))

            staff_embed = discord.Embed(
                title=f"EV Tracker Added",
                description="\n".join(staff_desc_lines),
                color=DEFAULT_EMBED_COLOR,
                timestamp=datetime.now(),
            )
            staff_embed = design_embed(
                embed=staff_embed, user=user, pokemon_name=pokemon_title
            )

            await send_webhook(
                bot=bot,
                channel=staff_channel,
                embed=staff_embed,
            )

    except Exception as e:
        pretty_log(
            tag="error",
            message=f"Failed to track EVs for user {user_id}: {e}",
        )
        await handle.error(content=f"Failed to track EVs: {e}")

import discord

from utils.cache.cache_list import timer_cache
from utils.db.timers_db import fetch_all_timers
from utils.logs.pretty_log import pretty_log


# 🟣────────────────────────────────────────────
#       🐭 Timer Cache Loader 🐭
# ─────────────────────────────────────────────
async def load_timer_cache(bot):
    """
    Load all user timer settings into memory cache.
    Uses the fetch_all_timers DB function.
    """
    timer_cache.clear()

    rows = await fetch_all_timers(bot)
    for row in rows:
        timer_cache[row["user_id"]] = {
            "user_name": row.get("user_name"),
            "pokemon_setting": row.get("pokemon_setting"),
            "fish_setting": row.get("fish_setting"),
            "battle_setting": row.get("battle_setting"),
        }

    # 🐭 Debug log
    pretty_log(
        message=f"Loaded {len(timer_cache)} users' timer settings into cache",
        tag="cache",

    )

    return timer_cache

def fetch_id_by_user_name(user_name: str):
    """
    Fetch a user ID from the timer cache based on the user name.
    """
    for user_id, settings in timer_cache.items():
        if settings.get("user_name") == user_name:
            return user_id
    return None

def upsert_timer_cache(
    user_id: int,
    user_name: str,
    pokemon_setting: str,
    fish_setting: str,
    battle_setting: str,
):
    """
    Update or insert a user's timer settings into the in-memory cache.
    """
    timer_cache[user_id] = {
        "user_name": user_name,
        "pokemon_setting": pokemon_setting,
        "fish_setting": fish_setting,
        "battle_setting": battle_setting,
    }
    pretty_log(
        message=f"Upserted timer settings for: {user_name} into cache",
        tag="cache",
    )

def update_pokemon_timer_setting(
    user_id: int,
    pokemon_setting: str,
):
    """
    Update a user's pokemon timer setting in the in-memory cache.
    """
    if user_id in timer_cache:
        timer_cache[user_id]["pokemon_setting"] = pokemon_setting
        pretty_log(
            message=f"Updated pokemon_setting for user_id: {user_id} in cache",
            tag="cache",
        )

def update_fish_timer_setting(
    user_id: int,
    fish_setting: str,
):
    """
    Update a user's fish timer setting in the in-memory cache.
    """
    if user_id in timer_cache:
        timer_cache[user_id]["fish_setting"] = fish_setting
        pretty_log(
            message=f"Updated fish_setting for user_id: {user_id} in cache",
            tag="cache",
        )

def update_battle_timer_setting(
    user_id: int,
    battle_setting: str,
):
    """
    Update a user's battle timer setting in the in-memory cache.
    """
    if user_id in timer_cache:
        timer_cache[user_id]["battle_setting"] = battle_setting
        pretty_log(
            message=f"Updated battle_setting for user_id: {user_id} in cache",
            tag="cache",
        )

def remove_user_from_timer_cache(user_id: int):
    """
    Remove a user's timer settings from the in-memory cache.
    """
    if user_id in timer_cache:
        del timer_cache[user_id]
        pretty_log(
            message=f"Removed user_id: {user_id} from timer cache",
            tag="cache",
        )
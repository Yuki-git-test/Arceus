import discord

from utils.cache.cache_list import weekly_goal_cache
from utils.db.weekly_goal_tracker import fetch_all_weekly_goals
from utils.logs.pretty_log import pretty_log


# Load Weekly Goal Cache
async def load_weekly_goal_cache(bot: discord.Client):
    """Loads all weekly goal records into the in-memory cache."""
    weekly_goal_cache.clear()
    rows = await fetch_all_weekly_goals(bot)
    for row in rows:
        user_id = row["user_id"]
        if user_id is None:
            continue

        weekly_goal_cache[row["user_id"]] = {
            "user_name": row.get("user_name"),
            "pokemon_caught": row.get("pokemon_caught", 0),
            "fish_caught": row.get("fish_caught", 0),
            "battles_won": row.get("battles_won", 0),
            "channel_id": row.get("channel_id"),
            "weekly_requirement_mark": row.get("weekly_requirement_mark", False),
        }

    pretty_log(
        "cache",
        message=f"Loaded {len(weekly_goal_cache)} users' weekly goal stats into cache",
        label="💠 WEEKLY GOAL CACHE",
        bot=bot,
    )
    return weekly_goal_cache


# 🟦────────────────────────────────────────────
#       💠 Cache Functions
# ─────────────────────────────────────────────
def upsert_weekly_goal_cache(
    user_id: int,
    user_name: str,
    pokemon_caught: int = 0,
    fish_caught: int = 0,
    battles_won: int = 0,
    channel_id: int | None = None,
    weekly_requirement_mark: bool = False,
):

    if user_id in weekly_goal_cache:
        # Update existing entry
        weekly_goal_cache[user_id]["pokemon_caught"] = pokemon_caught
        weekly_goal_cache[user_id]["fish_caught"] = fish_caught
        weekly_goal_cache[user_id]["battles_won"] = battles_won
        if channel_id is not None:
            weekly_goal_cache[user_id]["channel_id"] = channel_id
        weekly_goal_cache[user_id]["user_name"] = user_name
        weekly_goal_cache[user_id].setdefault("weekly_requirement_mark", False)
    else:
        # Insert new entry
        weekly_goal_cache[user_id] = {
            "pokemon_caught": pokemon_caught,
            "fish_caught": fish_caught,
            "battles_won": battles_won,
            "channel_id": channel_id,
            "user_name": user_name,
            "weekly_requirement_mark": False,
        }

    # Mark this user as dirty for flushing
    mark_weekly_goal_dirty(user_id)

    pretty_log(
        "info",
        f"Upserted weekly goals for {user_name}: "
        f"Pokémon Caught={pokemon_caught}, Fish Caught={fish_caught}, Battles Won={battles_won}",
        label="💠 WEEKLY GOAL CACHE",
    )


def update_weekly_requirement_mark(user_id: int, value: bool = True):
    """Set weekly_requirement_mark for a user."""
    if user_id not in weekly_goal_cache:
        weekly_goal_cache[user_id] = {
            "pokemon_caught": 0,
            "fish_caught": 0,
            "battles_won": 0,
            "channel_id": None,
            "user_name": f"User {user_id}",
            "weekly_requirement_mark": value,
        }
    else:
        weekly_goal_cache[user_id]["weekly_requirement_mark"] = value

    mark_weekly_goal_dirty(user_id)


def set_weekly_stats(
    user_id: int,
    user_name: str,
    pokemon_caught: int,
    fish_caught: int,
    battles_won: int,
):
    """
    Set the weekly stats for a user in the weekly_goal_cache.
    Updates Pokémon caught, fish caught, and battles won.
    """

    # Ensure user exists in the cache
    if user_id not in weekly_goal_cache:
        weekly_goal_cache[user_id] = {
            "pokemon_caught": 0,
            "fish_caught": 0,
            "battles_won": 0,
        }

    # Update all three stats
    weekly_goal_cache[user_id]["pokemon_caught"] = pokemon_caught
    weekly_goal_cache[user_id]["fish_caught"] = fish_caught
    weekly_goal_cache[user_id]["battles_won"] = battles_won
    mark_weekly_goal_dirty(user_id)

    pretty_log(
        "info",
        f"Set weekly stats for {user_name}: "
        f"Pokémon Caught={pokemon_caught}, Fish Caught={fish_caught}, Battles Won={battles_won}",
        label="💠 WEEKLY GOAL CACHE",
    )


def set_pokemon_caught(user: discord.Member, amount: int):
    """Set Pokémon caught to a specific amount."""
    user_id = user.id
    user_name = user.name

    if user_id not in weekly_goal_cache:
        weekly_goal_cache[user_id] = {
            "pokemon_caught": 0,
            "fish_caught": 0,
            "battles_won": 0,
        }

    weekly_goal_cache[user_id]["pokemon_caught"] = amount


def increment_fish_caught(user: discord.Member, amount: int = 1):
    """Increment fish caught by a given amount."""
    user_id = user.id
    user_name = user.name

    if user_id not in weekly_goal_cache:
        weekly_goal_cache[user_id] = {
            "pokemon_caught": 0,
            "fish_caught": 0,
            "battles_won": 0,
        }

    weekly_goal_cache[user_id]["fish_caught"] += amount


def increment_battles_won(user_name: str, user_id: int, amount: int = 1):
    """Increment battles won by a given amount."""

    if user_id not in weekly_goal_cache:
        weekly_goal_cache[user_id] = {
            "pokemon_caught": 0,
            "fish_caught": 0,
            "battles_won": 0,
        }

    weekly_goal_cache[user_id]["battles_won"] += amount


# 💠────────────────────────────────────────────
# [📦 HELPER] Bulk Flush Weekly Goal Cache -> DB (Dirty-Flag Version)
# 💠────────────────────────────────────────────

# Dictionary to track which users have updated stats
weekly_goal_cache_dirty: dict[int, bool] = {}


async def flush_weekly_goal_cache(bot: discord.Client):
    """
    Bulk upsert only dirty entries from weekly_goal_cache into the database.
    Call periodically (e.g., every 5 minutes) to persist cache.
    """
    if not weekly_goal_cache:
        return  # nothing to flush

    # Filter only dirty users
    dirty_users = [uid for uid, dirty in weekly_goal_cache_dirty.items() if dirty]

    # ── Exit early if nothing changed ──
    if not dirty_users:
        return  # nothing to flush

    query = """
        INSERT INTO weekly_goal_tracker (
            user_id, user_name, channel_id, pokemon_caught, fish_caught, battles_won,
            weekly_requirement_mark
        )
        VALUES ($1, $2, $3, $4, $5, $6, $7)
        ON CONFLICT(user_id) DO UPDATE SET
            user_name = EXCLUDED.user_name,
            channel_id = EXCLUDED.channel_id,
            pokemon_caught = EXCLUDED.pokemon_caught,
            fish_caught = EXCLUDED.fish_caught,
            battles_won = EXCLUDED.battles_won,
            weekly_requirement_mark = EXCLUDED.weekly_requirement_mark
    """

    async with bot.pg_pool.acquire() as conn:
        for user_id in dirty_users:
            stats = weekly_goal_cache[user_id]
            user_obj = bot.get_user(user_id)
            user_name = stats.get("user_name") or (
                user_obj.name if user_obj else f"User {user_id}"
            )
            channel_id = stats.get("channel_id")

            await conn.execute(
                query,
                user_id,
                user_name,
                channel_id,
                stats.get("pokemon_caught", 0),
                stats.get("fish_caught", 0),
                stats.get("battles_won", 0),
                stats.get("weekly_requirement_mark", False),
            )

            # Clear dirty flag after writing
            weekly_goal_cache_dirty[user_id] = False


# ── Helper to mark a user as dirty whenever stats change ──
def mark_weekly_goal_dirty(user_id: int):
    """Mark a user's weekly goal stats as dirty so they will be flushed to the DB.
    Exit early if already marked dirty.
    """
    if weekly_goal_cache_dirty.get(user_id):
        return  # already dirty, no need to set again
    weekly_goal_cache_dirty[user_id] = True


# 💠────────────────────────────────────────────
# [📦 HELPER] Fetch Weekly Goal From Cache by Name
# 💠────────────────────────────────────────────
def fetch_weekly_goal_cache_by_name(user_name: str):
    """
    Fetch a user's weekly goal stats from cache by Discord username.
    Returns a dict with user_id, pokemon_caught, fish_caught, battles_won, channel_id.
    """
    for user_id, stats in weekly_goal_cache.items():
        if stats.get("user_name") == user_name:
            return {
                "user_id": user_id,
                "pokemon_caught": stats.get("pokemon_caught", 0),
                "fish_caught": stats.get("fish_caught", 0),
                "battles_won": stats.get("battles_won", 0),
                "channel_id": stats.get("channel_id"),
            }
    return None


# 💠────────────────────────────────────────────
# [📦 HELPER] Fetch All Weekly Goal Cache
# 💠────────────────────────────────────────────
def fetch_all_weekly_goal_cache():
    """
    Returns a list of all weekly goal cache entries.
    Each entry is a dict containing:
        - user_id
        - user_name
        - pokemon_caught
        - fish_caught
        - battles_won
        - channel_id
    """
    all_entries = []
    for user_id, stats in weekly_goal_cache.items():
        all_entries.append(
            {
                "user_id": user_id,
                "user_name": stats.get("user_name"),
                "pokemon_caught": stats.get("pokemon_caught", 0),
                "fish_caught": stats.get("fish_caught", 0),
                "battles_won": stats.get("battles_won", 0),
                "channel_id": stats.get("channel_id"),
            }
        )
    return all_entries

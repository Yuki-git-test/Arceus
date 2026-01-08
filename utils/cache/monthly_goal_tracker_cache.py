import discord

from utils.cache.cache_list import monthly_goal_cache
from utils.db.monthly_goal_tracker import fetch_all_monthly_goals
from utils.logs.pretty_log import pretty_log


# Load monthly goals into cache
async def load_monthly_goal_cache(bot: discord.Client):
    """Loads all monthly goal records from the database into the in-memory cache."""
    try:
        monthly_goal_cache.clear()
        rows = await fetch_all_monthly_goals(bot)
        for row in rows:
            user_id = row["user_id"]
            if user_id is None:
                pretty_log("info", f"Skipping row with None user_id: {row}")
                continue  # Skip entries without a valid user_id
            monthly_goal_cache[user_id] = {
                "user_name": row["user_name"],
                "channel_id": row["channel_id"],
                "pokemon_caught": row["pokemon_caught"],
                "fish_caught": row["fish_caught"],
                "battles_won": row["battles_won"],
                "monthly_requirement_mark": row["monthly_requirement_mark"],
            }
        pretty_log(
            "cache",
            f"Loaded {len(monthly_goal_cache)} monthly goal records into cache.",
        )
        return monthly_goal_cache
    except Exception as e:
        pretty_log("error", f"Exception in load_monthly_goal_cache: {e}")
        raise


# 🟦────────────────────────────────────────────
#       💠 Cache Functions
# ─────────────────────────────────────────────
def upsert_monthly_goal_cache(
    user_id : int,
    user_name: str,
    pokemon_caught: int = 0,
    fish_caught: int = 0,
    battles_won: int = 0,
    channel_id: int | None = None,
    monthly_requirement_mark: bool = False,
):


    if user_id in monthly_goal_cache:
        # Update existing entry
        monthly_goal_cache[user_id]["pokemon_caught"] = pokemon_caught
        monthly_goal_cache[user_id]["fish_caught"] = fish_caught
        monthly_goal_cache[user_id]["battles_won"] = battles_won
        if channel_id is not None:
            monthly_goal_cache[user_id]["channel_id"] = channel_id
        monthly_goal_cache[user_id]["user_name"] = user_name
        monthly_goal_cache[user_id].setdefault("monthly_requirement_mark", False)
    else:
        # Insert new entry
        monthly_goal_cache[user_id] = {
            "pokemon_caught": pokemon_caught,
            "fish_caught": fish_caught,
            "battles_won": battles_won,
            "channel_id": channel_id,
            "user_name": user_name,
            "monthly_requirement_mark": False,
        }

    # Mark this user as dirty for flushing
    mark_monthly_goal_dirty(user_id)

    pretty_log(
        "info",
        f"Upserted monthly goals for {user_name}: "
        f"Pokémon Caught={pokemon_caught}, Fish Caught={fish_caught}, Battles Won={battles_won}",
        label="💠 MONTHLY GOAL CACHE",
    )


def update_monthly_requirement_mark(user_id: int, value: bool = True):
    """Set monthly_requirement_mark for a user."""
    if user_id not in monthly_goal_cache:
        monthly_goal_cache[user_id] = {
            "pokemon_caught": 0,
            "fish_caught": 0,
            "battles_won": 0,
            "channel_id": None,
            "user_name": f"User {user_id}",
            "monthly_requirement_mark": value,
        }
    else:
        monthly_goal_cache[user_id]["monthly_requirement_mark"] = value

    mark_monthly_goal_dirty(user_id)


def set_monthly_stats(
    user_id: int,
    user_name: str,
    pokemon_caught: int,
    fish_caught: int,
    battles_won: int,
):
    """
    Set the monthly stats for a user in the monthly_goal_cache.
    Updates Pokémon caught, fish caught, and battles won.
    """

    # Ensure user exists in the cache
    if user_id not in monthly_goal_cache:
        monthly_goal_cache[user_id] = {
            "pokemon_caught": 0,
            "fish_caught": 0,
            "battles_won": 0,
        }

    # Update all three stats
    monthly_goal_cache[user_id]["pokemon_caught"] = pokemon_caught
    monthly_goal_cache[user_id]["fish_caught"] = fish_caught
    monthly_goal_cache[user_id]["battles_won"] = battles_won
    mark_monthly_goal_dirty(user_id)

    pretty_log(
        "info",
        f"Set monthly stats for {user_name}: "
        f"Pokémon Caught={pokemon_caught}, Fish Caught={fish_caught}, Battles Won={battles_won}",
        label="💠 MONTHLY GOAL CACHE",
    )


def set_monthly_pokemon_caught(user: discord.Member, amount: int):
    """Set Pokémon caught to a specific amount."""
    user_id = user.id
    user_name = user.name

    if user_id not in monthly_goal_cache:
        monthly_goal_cache[user_id] = {
            "pokemon_caught": 0,
            "fish_caught": 0,
            "battles_won": 0,
        }

    monthly_goal_cache[user_id]["pokemon_caught"] = amount


def increment_monthly_fish_caught(user: discord.Member, amount: int = 1):
    """Increment fish caught by a given amount."""
    user_id = user.id
    user_name = user.name

    if user_id not in monthly_goal_cache:
        monthly_goal_cache[user_id] = {
            "pokemon_caught": 0,
            "fish_caught": 0,
            "battles_won": 0,
        }

    monthly_goal_cache[user_id]["fish_caught"] += amount


def increment_monthly_battles_won(user_name: str, user_id: int, amount: int = 1):
    """Increment battles won by a given amount."""

    if user_id not in monthly_goal_cache:
        monthly_goal_cache[user_id] = {
            "pokemon_caught": 0,
            "fish_caught": 0,
            "battles_won": 0,
        }

    monthly_goal_cache[user_id]["battles_won"] += amount


# 💠────────────────────────────────────────────
# [📦 HELPER] Bulk Flush MONTHLY GOAL CACHE -> DB (Dirty-Flag Version)
# 💠────────────────────────────────────────────

# Dictionary to track which users have updated stats
monthly_goal_cache_dirty: dict[int, bool] = {}


async def flush_monthly_goal_cache(bot: discord.Client):
    """
    Bulk upsert only dirty entries from monthly_goal_cache into the database.
    Call periodically (e.g., every 5 minutes) to persist cache.
    """
    if not monthly_goal_cache:
        return  # nothing to flush

    # Filter only dirty users
    dirty_users = [uid for uid, dirty in monthly_goal_cache_dirty.items() if dirty]

    # ── Exit early if nothing changed ──
    if not dirty_users:
        return  # nothing to flush

    query = """
        INSERT INTO monthly_goal_tracker (
            user_id, user_name, channel_id, pokemon_caught, fish_caught, battles_won,
            monthly_requirement_mark
        )
        VALUES ($1, $2, $3, $4, $5, $6, $7)
        ON CONFLICT(user_id) DO UPDATE SET
            user_name = EXCLUDED.user_name,
            channel_id = EXCLUDED.channel_id,
            pokemon_caught = EXCLUDED.pokemon_caught,
            fish_caught = EXCLUDED.fish_caught,
            battles_won = EXCLUDED.battles_won,
            monthly_requirement_mark = EXCLUDED.monthly_requirement_mark
    """

    async with bot.pg_pool.acquire() as conn:
        for user_id in dirty_users:
            stats = monthly_goal_cache[user_id]
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
                stats.get("monthly_requirement_mark", False),
            )

            # Clear dirty flag after writing
            monthly_goal_cache_dirty[user_id] = False


# ── Helper to mark a user as dirty whenever stats change ──
def mark_monthly_goal_dirty(user_id: int):
    """Mark a user's monthly goal stats as dirty so they will be flushed to the DB.
    Exit early if already marked dirty.
    """
    if monthly_goal_cache_dirty.get(user_id):
        return  # already dirty, no need to set again
    monthly_goal_cache_dirty[user_id] = True


# 💠────────────────────────────────────────────
# [📦 HELPER] Fetch monthly Goal From Cache by Name
# 💠────────────────────────────────────────────
def fetch_monthly_goal_cache_by_name(user_name: str):
    """
    Fetch a user's monthly goal stats from cache by Discord username.
    Returns a dict with user_id, pokemon_caught, fish_caught, battles_won, channel_id.
    """
    for user_id, stats in monthly_goal_cache.items():
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
# [📦 HELPER] Fetch All MONTHLY GOAL CACHE
# 💠────────────────────────────────────────────
def fetch_all_monthly_goal_cache():
    """
    Returns a list of all MONTHLY GOAL CACHE entries.
    Each entry is a dict containing:
        - user_id
        - user_name
        - pokemon_caught
        - fish_caught
        - battles_won
        - channel_id
    """
    all_entries = []
    for user_id, stats in monthly_goal_cache.items():
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

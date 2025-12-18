import discord

from utils.logs.pretty_log import pretty_log

# SQL SCRIPT
"""CREATE TABLE timers (
    user_id BIGINT PRIMARY KEY,
    user_name TEXT,
    pokemon_setting TEXT,
    fish_setting TEXT,
    battle_setting TEXT
);
"""


# Fetch all timer settings
async def fetch_all_timers(bot: discord.Client):
    try:
        async with bot.db_pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT user_id, user_name, pokemon_setting, fish_setting, battle_setting
                FROM timers
                """
            )
            timers = [
                {
                    "user_id": row["user_id"],
                    "user_name": row["user_name"],
                    "pokemon_setting": row["pokemon_setting"],
                    "fish_setting": row["fish_setting"],
                    "battle_setting": row["battle_setting"],
                }
                for row in rows
            ]
            pretty_log(message="✅ Fetched all timer settings", tag="db")
            return timers
    except Exception as e:
        pretty_log(message=f"❌ Error fetching timer settings - {e}", tag="db")
        return []


# Upsert Timer Settings
async def upsert_timer(
    bot: discord.Client,
    user_id: int,
    user_name: str,
):
    pokemon_setting = "off"
    fish_setting = "off"
    battle_setting = "off"
    try:
        async with bot.db_pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO timers (user_id, user_name, pokemon_setting, fish_setting, battle_setting)
                VALUES ($1, $2, $3, $4, $5)
                ON CONFLICT (user_id) DO UPDATE
                SET user_name = EXCLUDED.user_name
                """,
                user_id,
                user_name,
                pokemon_setting,
                fish_setting,
                battle_setting,
            )
            pretty_log(
                message=f"✅ Upserted timer settings for user_id: {user_id}",
                tag="db",
            )
            # Update in cache
            from utils.cache.timers_cache import upsert_timer_cache

            upsert_timer_cache(
                user_id,
                user_name,
                pokemon_setting,
                fish_setting,
                battle_setting,
            )

    except Exception as e:
        pretty_log(
            message=f"❌ Error upserting timer settings for user_id: {user_id} - {e}",
            tag="db",
        )


async def fetch_timer(bot, user_id: int):
    try:
        async with bot.db_pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT user_id, user_name, pokemon_setting, fish_setting, battle_setting
                FROM timers
                WHERE user_id = $1
                """,
                user_id,
            )
            if row:
                pretty_log(
                    message=f"✅ Fetched timer settings for user_id: {user_id}",
                    tag="db",
                )
                return {
                    "user_id": row["user_id"],
                    "user_name": row["user_name"],
                    "pokemon_setting": row["pokemon_setting"],
                    "fish_setting": row["fish_setting"],
                    "battle_setting": row["battle_setting"],
                }
            else:
                pretty_log(
                    message=f"⚠️ No timer settings found for user_id: {user_id}",
                    tag="db",
                )
                return None
    except Exception as e:
        pretty_log(
            message=f"❌ Error fetching timer settings for user_id: {user_id} - {e}",
            tag="db",
        )
        return None


async def update_pokemon_setting(
    bot,
    user_id: int,
    pokemon_setting: str,
):
    try:
        async with bot.db_pool.acquire() as conn:
            await conn.execute(
                """
                UPDATE timers
                SET pokemon_setting = $1
                WHERE user_id = $2
                """,
                pokemon_setting,
                user_id,
            )
            pretty_log(
                message=f"✅ Updated pokemon_setting for user_id: {user_id} to {pokemon_setting}",
                tag="db",
            )
            # Also update the cache
            from utils.cache.timers_cache import update_pokemon_timer_setting

            update_pokemon_timer_setting(user_id, pokemon_setting)

    except Exception as e:
        pretty_log(
            message=f"❌ Error updating pokemon_setting for user_id: {user_id} - {e}",
            tag="db",
        )


async def update_fish_setting(
    bot,
    user_id: int,
    fish_setting: str,
):
    try:
        async with bot.db_pool.acquire() as conn:
            await conn.execute(
                """
                UPDATE timers
                SET fish_setting = $1
                WHERE user_id = $2
                """,
                fish_setting,
                user_id,
            )
            pretty_log(
                message=f"✅ Updated fish_setting for user_id: {user_id} to {fish_setting}",
                tag="db",
            )
            # Also update the cache
            from utils.cache.timers_cache import update_fish_timer_setting

            update_fish_timer_setting(user_id, fish_setting)

    except Exception as e:
        pretty_log(
            message=f"❌ Error updating fish_setting for user_id: {user_id} - {e}",
            tag="db",
        )


async def update_battle_setting(
    bot,
    user_id: int,
    battle_setting: str,
):
    try:
        async with bot.db_pool.acquire() as conn:
            await conn.execute(
                """
                UPDATE timers
                SET battle_setting = $1
                WHERE user_id = $2
                """,
                battle_setting,
                user_id,
            )
            pretty_log(
                message=f"✅ Updated battle_setting for user_id: {user_id} to {battle_setting}",
                tag="db",
            )
            # Also update the cache
            from utils.cache.timers_cache import update_battle_timer_setting

            update_battle_timer_setting(user_id, battle_setting)

    except Exception as e:
        pretty_log(
            message=f"❌ Error updating battle_setting for user_id: {user_id} - {e}",
            tag="db",
        )


async def delete_timer(bot: discord.Client, user_id: int):
    try:
        async with bot.db_pool.acquire() as conn:
            await conn.execute(
                """
                DELETE FROM timers
                WHERE user_id = $1
                """,
                user_id,
            )
            pretty_log(
                message=f"✅ Deleted timer settings for user_id: {user_id}",
                tag="db",
            )
            # Also remove from cache
            from utils.cache.timers_cache import remove_user_from_timer_cache

            remove_user_from_timer_cache(user_id)

    except Exception as e:
        pretty_log(
            message=f"❌ Error deleting timer settings for user_id: {user_id} - {e}",
            tag="db",
        )

import discord

from utils.logs.pretty_log import pretty_log

# SQL Script
"""CREATE TABLE IF NOT EXISTS active_world_boss (
    id INTEGER PRIMARY KEY DEFAULT 1 CHECK (id = 1),
    wb_timestamp BIGINT NOT NULL,
    boss_name TEXT NOT NULL
);"""


async def upsert_active_wb(bot: discord.Client, wb_timestamp: int, boss_name: str):
    try:
        async with bot.pg_pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO active_world_boss (id, wb_timestamp, boss_name)
                VALUES (1, $1, $2)
                ON CONFLICT (id) DO UPDATE
                SET wb_timestamp = EXCLUDED.wb_timestamp,
                    boss_name = EXCLUDED.boss_name;
                """,
                wb_timestamp,
                boss_name,
            )
            from utils.cache.active_wb_cache import upsert_active_wb_cache

            upsert_active_wb_cache(boss_name, wb_timestamp)
            pretty_log(f"Upserted active world boss: {boss_name} at {wb_timestamp}")
    except Exception as e:
        pretty_log(f"Error upserting active world boss: {e}")


async def fetch_active_wb(bot: discord.Client):
    try:
        async with bot.pg_pool.acquire() as conn:
            row = await conn.fetchrow("""
                SELECT wb_timestamp, boss_name
                FROM active_world_boss
                WHERE id = 1;
                """)
            return row
    except Exception as e:
        pretty_log(f"Error fetching active world boss: {e}")
        return None


async def remove_active_wb(bot: discord.Client):
    try:
        async with bot.pg_pool.acquire() as conn:
            await conn.execute("""
                DELETE FROM active_world_boss
                WHERE id = 1;
                """)
            from utils.cache.active_wb_cache import remove_active_wb_cache

            remove_active_wb_cache()
            pretty_log("success", "Removed active world boss")
    except Exception as e:
        pretty_log(f"Error removing active world boss: {e}")

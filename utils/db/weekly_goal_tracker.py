# SQL Script
"""CREATE TABLE weekly_goal_tracker (
    user_id BIGINT,
    user_name VARCHAR(64) NOT NULL PRIMARY KEY,
    channel_id BIGINT,
    pokemon_caught INT,
    fish_caught INT,
    battles_won INT,
    weekly_requirement_mark BOOLEAN
);"""
import discord

from utils.logs.pretty_log import pretty_log


# Upsert Function
async def upsert_weekly_goal(
    bot: discord.Client,
    user_id: int,
    user_name: str,
    channel_id: int = None,
    pokemon_caught: int = 0,
    fish_caught: int = 0,
    battles_won: int = 0,
    weekly_requirement_mark: bool = False,
):
    """Upserts a weekly goal record for a user in the database."""
    async with bot.pg_pool.acquire() as conn:
        query = """
        INSERT INTO weekly_goal_tracker (
            user_id, user_name, channel_id,
            pokemon_caught, fish_caught,
            battles_won, weekly_requirement_mark
        ) VALUES ($1, $2, $3, $4, $5, $6, $7)
        ON CONFLICT (user_id) DO UPDATE SET
            user_name = EXCLUDED.user_name,
            channel_id = EXCLUDED.channel_id,
            pokemon_caught = EXCLUDED.pokemon_caught,
            fish_caught = EXCLUDED.fish_caught,
            battles_won = EXCLUDED.battles_won,
            weekly_requirement_mark = EXCLUDED.weekly_requirement_mark;
        """
        await conn.execute(
            query,
            user_id,
            user_name,
            channel_id,
            pokemon_caught,
            fish_caught,
            battles_won,
            weekly_requirement_mark,
        )
        pretty_log("db", f"Upserted weekly goal for user: {user_name}")
        # Upsert in cache as well
        from utils.cache.weekly_goal_tracker_cache import upsert_weekly_goal_cache

        upsert_weekly_goal_cache(
            user_id=user_id,
            user_name=user_name,
            channel_id=channel_id,
            pokemon_caught=pokemon_caught,
            fish_caught=fish_caught,
            battles_won=battles_won,
            weekly_requirement_mark=weekly_requirement_mark,
        )


async def fetch_all_weekly_goals(bot: discord.Client) -> list[dict]:
    """Fetches all weekly goal records from the database."""
    async with bot.pg_pool.acquire() as conn:
        query = "SELECT * FROM weekly_goal_tracker;"
        records = await conn.fetch(query)
        pretty_log("db", f"Fetched {len(records)} weekly goal records.")
        return [dict(record) for record in records]


async def delete_all_weekly_goals(bot: discord.Client):
    """Deletes all weekly goal records from the database."""
    async with bot.pg_pool.acquire() as conn:
        query = "DELETE FROM weekly_goal_tracker;"
        await conn.execute(query)
        pretty_log("db", "Deleted all weekly goal records.")

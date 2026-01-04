import time

import discord

from utils.logs.pretty_log import pretty_log

# SQL Script
"""CREATE TABLE IF NOT EXISTS shiny_bonus (
    message_id BIGINT PRIMARY KEY,
    started_on BIGINT,
    ends_on BIGINT
);"""


async def upsert_shiny_bonus(
    bot,
    message_id: int,
    started_on: int,
    ends_on: int,
):
    try:
        async with bot.pg_pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO shiny_bonus (id, message_id, started_on, ends_on)
                VALUES (1, $1, $2, $3)
                ON CONFLICT (id)
                DO UPDATE SET message_id = EXCLUDED.message_id,
                              started_on = EXCLUDED.started_on,
                              ends_on = EXCLUDED.ends_on
                """,
                message_id,
                started_on,
                ends_on,
            )
            pretty_log(
                "info",
                f"Upserted shiny bonus message ID {message_id}",
            )
    except Exception as e:
        pretty_log(
            "warn",
            f"Failed to upsert shiny bonus message ID {message_id}: {e}",
        )


async def update_shiny_bonus_ends_on(
    bot,
    message_id: int,
    ends_on: int,
):
    try:
        async with bot.pg_pool.acquire() as conn:
            await conn.execute(
                """
                UPDATE shiny_bonus
                SET ends_on = $1
                WHERE message_id = $2
                """,
                ends_on,
                message_id,
            )
            pretty_log(
                "info",
                f"Updated shiny bonus ends_on for message ID {message_id}",
            )
    except Exception as e:
        pretty_log(
            "warn",
            f"Failed to update shiny bonus ends_on for message ID {message_id}: {e}",
        )


async def fetch_shiny_bonus(bot) -> dict[str, int] | None:
    try:
        async with bot.pg_pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT message_id, started_on, ends_on FROM shiny_bonus
                WHERE id = 1
                """,
            )
            if row:
                return {
                    "message_id": row["message_id"],
                    "started_on": row["started_on"],
                    "ends_on": row["ends_on"],
                }
            else:
                pretty_log(
                    "info",
                    f"No shiny bonus record found",
                )
                return None
    except Exception as e:
        pretty_log(
            "warn",
            f"Failed to fetch shiny bonus record: {e}",
        )
        return None

async def update_shiny_bonus_message_id(
    bot,
    message_id: int,
):
    try:
        async with bot.pg_pool.acquire() as conn:
            await conn.execute(
                """
                UPDATE shiny_bonus
                SET message_id = $1
                WHERE id = 1
                """,
                message_id,
            )
            pretty_log(
                "info",
                f"Updated shiny bonus message ID to {message_id}",
            )
    except Exception as e:
        pretty_log(
            "warn",
            f"Failed to update shiny bonus message ID to {message_id}: {e}",
        )

async def extend_shiny_bonus(
    bot,
    seconds: int,
):
    try:
        async with bot.pg_pool.acquire() as conn:
            await conn.execute(
                """
                UPDATE shiny_bonus
                SET ends_on = ends_on + $1
                WHERE id = 1
                """,
                seconds,
            )
            pretty_log(
                "info",
                f"Extended shiny bonus by {seconds} seconds",
            )
    except Exception as e:
        pretty_log(
            "warn",
            f"Failed to extend shiny bonus by {seconds} seconds: {e}",
        )

async def delete_shiny_bonus(bot):
    try:
        async with bot.pg_pool.acquire() as conn:
            await conn.execute(
                """
                DELETE FROM shiny_bonus
                WHERE id = 1
                """,
            )
            pretty_log(
                "info",
                f"Deleted shiny bonus record",
            )
    except Exception as e:
        pretty_log(
            "warn",
            f"Failed to delete shiny bonus record: {e}",
        )

async def fetch_ends_on(bot) -> int | None:
    try:
        async with bot.pg_pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT ends_on FROM shiny_bonus
                WHERE id = 1
                """,
            )
            if row:
                return row["ends_on"]
            else:
                pretty_log(
                    "info",
                    f"No shiny bonus ends_on found",
                )
                return None
    except Exception as e:
        pretty_log(
            "warn",
            f"Failed to fetch shiny bonus ends_on: {e}",
        )
        return None
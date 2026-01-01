

import discord

from utils.logs.pretty_log import pretty_log

# SQL SCRIPT
"""CREATE TABLE IF NOT EXISTS ping_message_ids (
    message_id BIGINT,
    type TEXT PRIMARY KEY
);"""


async def upsert_ping_message_id(bot, message_id: int, type: str):
    try:
        async with bot.pg_pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO ping_message_ids (message_id, type)
                VALUES ($1, $2)
                ON CONFLICT (type)
                DO UPDATE SET message_id = EXCLUDED.message_id
                """,
                message_id,
                type,
            )
            pretty_log(
                "info",
                f"Upserted ping message ID {message_id} for type {type}",
            )
            # Update cache as well
            from utils.cache.ping_message_id_cache import upsert_ping_message_id_cache

            upsert_ping_message_id_cache(type, message_id)
    except Exception as e:
        pretty_log(
            "warn",
            f"Failed to upsert ping message ID for type {type}: {e}",
        )


async def get_ping_message_id(bot, type: str) -> int | None:
    try:
        async with bot.pg_pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT message_id FROM ping_message_ids
                WHERE type = $1
                """,
                type,
            )
            if row:
                return row["message_id"]
            else:
                pretty_log(
                    "info",
                    f"No ping message ID found for type {type}",
                )
                return None
    except Exception as e:
        pretty_log(
            "warn",
            f"Failed to get ping message ID for type {type}: {e}",
        )
        return None


async def delete_ping_message_id(bot, type: str):
    try:
        async with bot.pg_pool.acquire() as conn:
            await conn.execute(
                """
                DELETE FROM ping_message_ids
                WHERE type = $1
                """,
                type,
            )
            pretty_log(
                "info",
                f"Deleted ping message ID for type {type}",
            )
            # Update cache as well
            from utils.cache.ping_message_id_cache import delete_ping_message_id_cache

            delete_ping_message_id_cache(type)

    except Exception as e:
        pretty_log(
            "warn",
            f"Failed to delete ping message ID for type {type}: {e}",
        )


async def fetch_all_ping_message_ids(
    bot,
) -> dict[str, int]:
    try:
        async with bot.pg_pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT type, message_id FROM ping_message_ids
                """
            )
            result = {row["type"]: row["message_id"] for row in rows}
            pretty_log(
                "info",
                f"Fetched all ping message IDs: {result}",
            )
            return result
    except Exception as e:
        pretty_log(
            "warn",
            f"Failed to fetch all ping message IDs: {e}",
        )
        return {}

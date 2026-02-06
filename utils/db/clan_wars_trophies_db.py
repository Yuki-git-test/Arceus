import discord

from Constants.clan_wars_constants import CLAN_WARS_TEXT_CHANNELS
from utils.logs.pretty_log import pretty_log

# SQL to create the clan_wars_trophies table
"""CREATE TABLE clan_wars_trophies (
    role_id   BIGINT PRIMARY KEY,
    clan_name VARCHAR(100) NOT NULL,
    amount    INT NOT NULL
);"""
TABLE_NAME = "clan_wars_trophies"

LEADERBOARD_CHANNEL_ID = CLAN_WARS_TEXT_CHANNELS.point_leaderboard


async def fetch_current_leaderboard_info(bot):
    """
    Fetch the trophy leaderboard info.
    Returns None if not found.
    """

    async with bot.pg_pool.acquire() as conn:
        return await conn.fetchrow(
            """
            SELECT * FROM current_trophy_leaderboard
            WHERE channel_id = $1
            LIMIT 1;
            """,
            LEADERBOARD_CHANNEL_ID,
        )


# Upsert row if table is empty
async def upsert_leaderboard_msg_id(bot, message_id: int, channel: discord.TextChannel):
    """
    Upsert the trophy leaderboard message ID.
    """
    channel_name = channel.name
    channel_id = channel.id
    async with bot.pg_pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO current_trophy_leaderboard (message_id, channel_id, channel_name)
            VALUES ($1, $2, $3)
            ON CONFLICT (message_id) DO UPDATE
            SET channel_id = EXCLUDED.channel_id,
                channel_name = EXCLUDED.channel_name;
            """,
            message_id,
            channel_id,
            channel_name,
        )
        pretty_log(
            "info",
            f"Upserted leaderboard message ID: {message_id} in channel {channel_name} ({channel_id})",
            label="Trophy Leaderboard DB",
        )


async def remove_leaderboard_msg_id(bot):
    """
    Remove the trophy leaderboard message ID.
    """
    async with bot.pg_pool.acquire() as conn:
        await conn.execute(
            """
            DELETE FROM current_trophy_leaderboard
            WHERE channel_id = $1;
            """,
            LEADERBOARD_CHANNEL_ID,
        )
        pretty_log(
            "info",
            f"Removed leaderboard message ID for channel ID: {LEADERBOARD_CHANNEL_ID}",
            label="Trophy Leaderboard DB",
        )


async def delete_all_clan_wars_trophies(bot: discord.Client):
    """Deletes all clan wars trophy records from the database."""
    try:
        async with bot.pg_pool.acquire() as conn:
            query = f"""
                DELETE FROM {TABLE_NAME};
            """
            await conn.execute(query)
            pretty_log(
                tag="db",
                message="Deleted all clan wars trophies from the database",
            )
            # Reset the leaderboard message ID as well
            await remove_leaderboard_msg_id(bot)

    except Exception as e:
        pretty_log(tag="error", message=f"Error deleting all clan wars trophies: {e}")


async def upsert_clan_wars_trophy(
    bot: discord.Client, role_id: int, clan_name: str, amount: int
):
    """Inserts or updates a clan wars trophy record in the database."""
    try:
        async with bot.pg_pool.acquire() as conn:
            query = f"""
                INSERT INTO {TABLE_NAME} (role_id, clan_name, amount)
                VALUES ($1, $2, $3)
                ON CONFLICT (role_id) DO UPDATE
                SET clan_name = EXCLUDED.clan_name,
                    amount = EXCLUDED.amount;
            """
            await conn.execute(query, role_id, clan_name, amount)
            pretty_log(
                tag="db",
                message=f"Upserted clan wars trophy: {clan_name} ({role_id}) - {amount}",
            )
    except Exception as e:
        pretty_log(tag="error", message=f"Error upserting clan wars trophy: {e}")


async def fetch_clan_wars_trophy(
    bot: discord.Client, role_id: int
) -> dict[str, int] | None:
    """Fetches a clan wars trophy record from the database by role_id."""
    try:
        async with bot.pg_pool.acquire() as conn:
            query = f"""
                SELECT clan_name, amount
                FROM {TABLE_NAME}
                WHERE role_id = $1;
            """
            row = await conn.fetchrow(query, role_id)
            if row:
                pretty_log(
                    tag="db",
                    message=f"Fetched clan wars trophy: {row['clan_name']} ({role_id}) - {row['amount']}",
                )
                return {"clan_name": row["clan_name"], "amount": row["amount"]}
            else:
                pretty_log(
                    tag="db",
                    message=f"No clan wars trophy found for role_id: {role_id}",
                )
                return None
    except Exception as e:
        pretty_log(tag="error", message=f"Error fetching clan wars trophy: {e}")
        return None


async def fetch_all_clan_wars_trophies(
    bot: discord.Client,
) -> dict[int, dict[str, int]]:
    """Fetches all clan wars trophies from the database and returns as a dictionary."""
    try:
        async with bot.pg_pool.acquire() as conn:
            query = f"""
                SELECT role_id, clan_name, amount
                FROM {TABLE_NAME};
            """
            rows = await conn.fetch(query)
            trophies = {
                row["role_id"]: {
                    "clan_name": row["clan_name"],
                    "amount": row["amount"],
                }
                for row in rows
            }
            pretty_log(
                tag="db",
                message=f"Fetched {len(trophies)} clan wars trophies from the database",
            )
            return trophies
    except Exception as e:
        pretty_log(tag="error", message=f"Error fetching clan wars trophies: {e}")
        return {}


async def delete_clan_wars_trophy(bot: discord.Client, role_id: int):
    """Deletes a clan wars trophy record from the database."""
    try:
        async with bot.pg_pool.acquire() as conn:
            query = f"""
                DELETE FROM {TABLE_NAME}
                WHERE role_id = $1;
            """
            await conn.execute(query, role_id)
            pretty_log(
                tag="db",
                message=f"Deleted clan wars trophy with role_id: {role_id}",
            )
    except Exception as e:
        pretty_log(tag="error", message=f"Error deleting clan wars trophy: {e}")

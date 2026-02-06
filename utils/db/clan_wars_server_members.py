import discord

from utils.logs.pretty_log import pretty_log

# SQL SCRIPT
"""CREATE TABLE clan_wars_server_members (
    user_id BIGINT PRIMARY KEY,
    user_name VARCHAR(255) NOT NULL,
    clan_name VARCHAR(255) NULL
);"""


async def fetch_all_clan_wars_server_members(
    bot: discord.Client,
) -> dict[int, dict[str, str | None]]:
    """Fetch all clan wars server members from the database and return as a dictionary."""
    try:
        async with bot.pg_pool.acquire() as conn:
            query = """
                SELECT user_id, user_name, clan_name
                FROM clan_wars_server_members;
            """
            rows = await conn.fetch(query)
            members = {
                row["user_id"]: {
                    "user_name": row["user_name"],
                    "clan_name": row["clan_name"],
                }
                for row in rows
            }
            pretty_log(
                f"Fetched {len(members)} clan wars server members from the database"
            )
            return members
    except Exception as e:
        pretty_log(f"Error fetching clan wars server members: {e}")
        return {}


async def upsert_clan_wars_server_member(
    bot: discord.Client,
    user_id: int,
    user_name: str,
    clan_name: str = None,
):
    """Insert or update a clan wars server member record in the database."""
    try:
        async with bot.pg_pool.acquire() as conn:
            query = """
                INSERT INTO clan_wars_server_members (user_id, user_name, clan_name)
                VALUES ($1, $2, $3)
                ON CONFLICT (user_id) DO UPDATE
                SET user_name = EXCLUDED.user_name,
                    clan_name = EXCLUDED.clan_name;
            """
            await conn.execute(query, user_id, user_name, clan_name)
            pretty_log(f"Upserted clan wars server member: {user_name} ({user_id})")
            # Update cache as well
            from utils.cache.clan_wars_cache import upsert_clan_wars_server_member_cache

            upsert_clan_wars_server_member_cache(user_id, user_name, clan_name)
    except Exception as e:
        pretty_log(
            f"Error upserting clan wars server member {user_name} ({user_id}): {e}"
        )


async def get_member_clan_name(
    bot: discord.Client,
    user_id: int,
) -> str | None:
    """Retrieve the clan name of a clan wars server member from the database."""
    try:
        async with bot.pg_pool.acquire() as conn:
            query = """
                SELECT clan_name
                FROM clan_wars_server_members
                WHERE user_id = $1;
            """
            row = await conn.fetchrow(query, user_id)
            if row:
                return row["clan_name"]
            return None
    except Exception as e:
        pretty_log(f"Error retrieving clan name for user_id {user_id}: {e}")
        return None


async def delete_clan_wars_server_member(
    bot: discord.Client,
    user_id: int,
):
    """Delete a clan wars server member record from the database."""
    try:
        async with bot.pg_pool.acquire() as conn:
            query = """
                DELETE FROM clan_wars_server_members
                WHERE user_id = $1;
            """
            await conn.execute(query, user_id)
            pretty_log(f"Deleted clan wars server member with user_id: {user_id}")
            # Remove from cache as well
            from utils.cache.clan_wars_cache import remove_member_from_cache

            remove_member_from_cache(user_id)
    except Exception as e:
        pretty_log(
            f"Error deleting clan wars server member with user_id {user_id}: {e}"
        )

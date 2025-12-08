import discord

from utils.logs.pretty_log import pretty_log

# SQL SCRIPT
"""CREATE TABLE faction_members (
    clan_name TEXT NOT NULL,
    user_id BIGINT NOT NULL,
    user_name TEXT NOT NULL,
    faction TEXT,
    notify TEXT,
    PRIMARY KEY (clan_name, user_id)
);"""


async def upsert_faction_member(
    bot,
    clan_name: str,
    user_id: int,
    user_name: str,
    faction: str = None,
    notify: str = None,
):
    """Upsert a faction member into the database."""
    try:
        async with bot.pg_pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO faction_members (clan_name, user_id, user_name, faction, notify)
                VALUES ($1, $2, $3, $4, $5)
                ON CONFLICT (clan_name, user_id)
                DO UPDATE SET user_name = EXCLUDED.user_name,
                              faction = EXCLUDED.faction,
                              notify = EXCLUDED.notify;
                """,
                clan_name,
                user_id,
                user_name,
                faction,
                notify,
            )
        pretty_log(
            tag="db",
            message=f"Upserted faction member {user_name} ({user_id}) in clan {clan_name}",
            bot=bot,
        )
        # Also update the cache
        from utils.cache.faction_members_cache import upsert_faction_member_into_cache

        upsert_faction_member_into_cache(
            user_id,
            user_name,
            clan_name,
            faction,
            notify,
        )
    except Exception as e:
        pretty_log(
            tag="error",
            message=f"Failed to upsert faction member {user_name} ({user_id}) in clan {clan_name}: {e}",
            bot=bot,
        )

async def fetch_faction_member(bot, user_id: int) -> dict | None:
    """Fetch a single faction member by user ID."""
    try:
        async with bot.pg_pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM faction_members WHERE user_id = $1", user_id
            )
            if row:
                member = dict(row)
                pretty_log(
                    tag="db",
                    message=f"Fetched faction member with user ID {user_id}",
                    bot=bot,
                )
                return member
            else:
                pretty_log(
                    tag="db",
                    message=f"No faction member found with user ID {user_id}",
                    bot=bot,
                )
                return None
    except Exception as e:
        pretty_log(
            tag="error",
            message=f"Failed to fetch faction member with user ID {user_id}: {e}",
            bot=bot,
        )
        return None


async def fetch_faction_members(bot) -> list[dict]:
    """Fetch all faction members from the database."""
    try:
        async with bot.pg_pool.acquire() as conn:
            rows = await conn.fetch("SELECT * FROM faction_members")
            members = [dict(row) for row in rows]
        pretty_log(
            tag="db",
            message=f"Fetched {len(members)} faction members from the database",
            bot=bot,
        )
        return members
    except Exception as e:
        pretty_log(
            tag="error",
            message=f"Failed to fetch faction members: {e}",
            bot=bot,
        )
        return []

async def update_faction_member_notify(
    bot,
    user_id: int,
    notify: str,
):
    """Update the notify preference for a faction member."""
    try:
        async with bot.pg_pool.acquire() as conn:
            await conn.execute(
                """
                UPDATE faction_members
                SET notify = $1
                WHERE user_id = $2;
                """,
                notify,
                user_id,
            )
        pretty_log(
            tag="db",
            message=f"Updated notify preference for faction member with user ID {user_id} to {notify}",
            bot=bot,
        )
        # Also update the cache
        from utils.cache.faction_members_cache import (
            update_faction_member_notify_in_cache,
        )

        update_faction_member_notify_in_cache(user_id, notify)

    except Exception as e:
        pretty_log(
            tag="error",
            message=f"Failed to update notify preference for faction member with user ID {user_id}: {e}",
            bot=bot,
        )


async def update_faction_member_faction(
    bot,
    user_id: int,
    faction: str,
):
    """Update the faction for a faction member."""
    try:
        async with bot.pg_pool.acquire() as conn:
            await conn.execute(
                """
                UPDATE faction_members
                SET faction = $1
                WHERE user_id = $2;
                """,
                faction,
                user_id,
            )
        pretty_log(
            tag="db",
            message=f"Updated faction for faction member with user ID {user_id} to {faction}",
            bot=bot,
        )
        # Also update the cache
        from utils.cache.faction_members_cache import (
            update_faction_member_faction_in_cache,
        )

        update_faction_member_faction_in_cache(user_id, faction)
    except Exception as e:
        pretty_log(
            tag="error",
            message=f"Failed to update faction for faction member with user ID {user_id}: {e}",
            bot=bot,
        )


async def remove_faction_member(bot, user_id: int):
    """Remove a faction member from the database."""
    try:
        async with bot.pg_pool.acquire() as conn:
            await conn.execute(
                "DELETE FROM faction_members WHERE user_id = $1", user_id
            )
        pretty_log(
            tag="db",
            message=f"Removed faction member with user ID {user_id}",
            bot=bot,
        )
        # Also remove from the cache
        from utils.cache.faction_members_cache import remove_faction_member_from_cache
        remove_faction_member_from_cache(user_id)
    except Exception as e:
        pretty_log(
            tag="error",
            message=f"Failed to remove faction member with user ID {user_id}: {e}",
            bot=bot,
        )

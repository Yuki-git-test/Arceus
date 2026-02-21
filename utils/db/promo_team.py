import discord

from utils.logs.pretty_log import pretty_log

# Sql Script
"""CREATE TABLE promo_team (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    promo_mon TEXT,
    egg_mon TEXT,
    instructions TEXT,
    ends_on BIGINT,
    image_link TEXT,
    thumbnail_link TEXT
);"""


async def upsert_promo_team(
    bot: discord.Client,
    promo_mon: str,
    egg_mon: str,
    instructions: str,
    image_link: str,
    thumbnail_link: str,
):
    try:
        async with bot.pg_pool.acquire() as conn:
            await conn.execute(
                """
                    INSERT INTO promo_team (id, promo_mon, egg_mon, instructions, image_link, thumbnail_link)
                    VALUES (1, $1, $2, $3, $4, $5)
                    ON CONFLICT (id)
                    DO UPDATE SET promo_mon = EXCLUDED.promo_mon,
                                egg_mon = EXCLUDED.egg_mon,
                                instructions = EXCLUDED.instructions,
                                image_link = EXCLUDED.image_link,
                                thumbnail_link = EXCLUDED.thumbnail_link
                    """,
                promo_mon,
                egg_mon,
                instructions,
                image_link,
                thumbnail_link,
            )
            pretty_log(
                "info",
                f"Upserted promo team: {promo_mon}, {egg_mon}",
            )
    except Exception as e:
        pretty_log(
            "warn",
            f"Failed to upsert promo team: {e}",
        )
async def get_promo_mon(bot: discord.Client) -> str | None:
    try:
        async with bot.pg_pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT promo_mon FROM promo_team
                WHERE id = 1
                """,
            )
            if row:
                return row["promo_mon"]
            else:
                pretty_log(
                    "info",
                    "No promo team found in database.",
                )
                return None
    except Exception as e:
        pretty_log(
            "warn",
            f"Failed to get promo team: {e}",
        )
        return None
    
async def get_promo_team(bot: discord.Client):
    try:
        async with bot.pg_pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT promo_mon, egg_mon, instructions, image_link, thumbnail_link
                FROM promo_team
                WHERE id = 1
                """,
            )
            if row:
                return {
                    "promo_mon": row["promo_mon"],
                    "egg_mon": row["egg_mon"],
                    "instructions": row["instructions"],
                    "image_link": row["image_link"],
                    "thumbnail_link": row["thumbnail_link"],
                }
            else:
                pretty_log(
                    "info",
                    "No promo team found in database.",
                )
                return None
    except Exception as e:
        pretty_log(
            "warn",
            f"Failed to get promo team: {e}",
        )
        return None

async def delete_promo_team(bot: discord.Client):
    try:
        async with bot.pg_pool.acquire() as conn:
            await conn.execute(
                """
                DELETE FROM promo_team
                WHERE id = 1
                """,
            )
            pretty_log(
                "info",
                "Deleted promo team from database.",
            )
    except Exception as e:
        pretty_log(
            "warn",
            f"Failed to delete promo team: {e}",
        )

async def update_promo_team_ends_on(bot: discord.Client, ends_on: int):
    try:
        async with bot.pg_pool.acquire() as conn:
            await conn.execute(
                """
                UPDATE promo_team
                SET ends_on = $1
                WHERE id = 1
                """,
                ends_on,
            )
            pretty_log(
                "info",
                f"Updated promo team ends_on to {ends_on}",
            )
    except Exception as e:
        pretty_log(
            "warn",
            f"Failed to update promo team ends_on: {e}",
        )

async def fetch_due_ends_on(bot: discord.Client) -> int | None:
    """Fetches the ends_on timestamp for the promo team, but only if it's due (i.e. ends_on is in the past)."""
    try:
        async with bot.pg_pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT ends_on FROM promo_team
                WHERE id = 1 AND ends_on <= EXTRACT(EPOCH FROM NOW())
                """,
            )
            if row:
                return row["ends_on"]
            else:
                pretty_log(
                    "info",
                    "No due promo team found in database.",
                )
                return None
    except Exception as e:
        pretty_log(
            "warn",
            f"Failed to fetch due promo team ends_on: {e}",
        )
        return None
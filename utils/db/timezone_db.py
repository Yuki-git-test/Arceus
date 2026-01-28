import discord
import pytz
from discord import app_commands

from utils.logs.pretty_log import pretty_log

# ==================================================
# 💜 TIMEZONE DB FUNCTIONS
# ==================================================


# -------------------- [💙 AUTOCOMPLETE] --------------------
async def tz_autocomplete(
    interaction: discord.Interaction, current: str
) -> list[app_commands.Choice[str]]:
    matches = autocomplete_timezones(current)
    return [app_commands.Choice(name=tz, value=tz) for tz in matches]


# -------------------- [💙 VALIDATE] --------------------
def is_valid_timezone(tz: str) -> bool:
    """Check if a given string is a valid IANA timezone."""
    return tz in pytz.all_timezones


# -------------------- [💙 AUTOCOMPLETE LIST] --------------------
def autocomplete_timezones(current: str) -> list[str]:
    """Return a list of matching timezones for autocomplete."""
    current_lower = current.lower()
    matches = [tz for tz in pytz.all_timezones if current_lower in tz.lower()]
    return matches[:25]  # Discord limits autocomplete to 25 suggestions


# -------------------- [💙 SET/UPDATE] --------------------
async def set_user_timezone(
    bot: discord.Client, user_id: int, user_name: str, timezone: str
):
    """Insert or update a user's timezone."""
    query = """
        INSERT INTO user_timezones(user_id, user_name, timezone, updated_at)
        VALUES ($1, $2, $3, NOW())
        ON CONFLICT(user_id) DO UPDATE
        SET timezone = EXCLUDED.timezone,
            user_name = EXCLUDED.user_name,
            updated_at = NOW()
    """
    async with bot.pg_pool.acquire() as conn:
        await conn.execute(query, user_id, user_name, timezone)
    pretty_log(
        "db",
        f"🌙 Set/Updated timezone for {user_name} ({user_id}) → {timezone}",
    )


# -------------------- [💙 REMOVE] --------------------
async def remove_user_timezone(bot: discord.Client, user_id: int):
    """Remove a user's timezone from the database."""
    query = "DELETE FROM user_timezones WHERE user_id = $1"
    async with bot.pg_pool.acquire() as conn:
        await conn.execute(query, user_id)
    pretty_log(
        "db",
        f"🌙 Removed timezone for user_id {user_id}",
    )


# -------------------- [💙 FETCH] --------------------
async def fetch_user_timezone(bot: discord.Client, user_id: int) -> str | None:
    """Fetch a user's timezone. Returns None if not set."""
    query = "SELECT timezone FROM user_timezones WHERE user_id = $1"
    async with bot.pg_pool.acquire() as conn:
        row = await conn.fetchrow(query, user_id)
    return row["timezone"] if row else None

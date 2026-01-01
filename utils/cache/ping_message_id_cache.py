import discord

from utils.cache.cache_list import ping_message_id_cache
from utils.db.ping_message_ids_db import fetch_all_ping_message_ids
from utils.logs.pretty_log import pretty_log


async def load_ping_message_id_cache(bot):
    """Load all ping message IDs from the database into the cache."""
    try:
        ping_ids = await fetch_all_ping_message_ids(bot)
        ping_message_id_cache.clear()
        for type, message_id in ping_ids.items():
            ping_message_id_cache[type] = message_id
        pretty_log(
            "info",
            f"Loaded {len(ping_message_id_cache)} ping message IDs into cache",
        )
    except Exception as e:
        pretty_log(
            "warn",
            f"Failed to load ping message ID cache: {e}",
        )


def upsert_ping_message_id_cache(type: str, message_id: int):
    """Insert or update a ping message ID in the cache."""
    ping_message_id_cache[type] = message_id
    pretty_log(
        "info",
        f"Upserted ping message ID in cache: type={type}, message_id={message_id}",
    )


def delete_ping_message_id_cache(type: str):
    """Delete a ping message ID from the cache."""
    if type in ping_message_id_cache:
        del ping_message_id_cache[type]
        pretty_log(
            "info",
            f"Deleted ping message ID from cache for type={type}",
        )
    else:
        pretty_log(
            "info",
            f"No ping message ID found in cache for type={type} to delete",
        )


def get_ping_message_id_incense() -> int | None:
    """Get the ping message ID for incense from the cache."""
    return ping_message_id_cache.get("incense", None)
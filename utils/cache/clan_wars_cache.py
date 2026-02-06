import discord

from utils.cache.cache_list import clan_wars_server_members_cache
from utils.db.clan_wars_server_members import fetch_all_clan_wars_server_members
from utils.logs.pretty_log import pretty_log


async def load_clan_wars_server_members_cache(bot: discord.Client):
    """Load clan wars server members from the database into the cache."""
    members = await fetch_all_clan_wars_server_members(bot)
    clan_wars_server_members_cache.clear()
    clan_wars_server_members_cache.update(members)

    if clan_wars_server_members_cache:
        # Print 1 to 2 sample entries from the cache for verification
        pretty_log("info", "Sample clan wars server members in cache:")
        for i, (user_id, member_info) in enumerate(
            clan_wars_server_members_cache.items()
        ):
            if i >= 2:
                break
            pretty_log(
                "info",
                f"User ID: {user_id}, User Name: {member_info['user_name']}, Clan Name: {member_info['clan_name']}",
            )
    pretty_log(f"Loaded {len(members)} clan wars server members into cache")
    return clan_wars_server_members_cache


def upsert_clan_wars_server_member_cache(
    user_id: int,
    user_name: str,
    clan_name: str | None,
):
    """Insert or update a clan wars server member record in the cache."""
    clan_wars_server_members_cache[user_id] = {
        "user_name": user_name,
        "clan_name": clan_name,
    }
    pretty_log(
        tag="cache",
        message=f"Upserted clan wars server member in cache: {user_name} ({user_id})",
    )

def get_member_clan_name_cache(user_id: int) -> str | None:
    """Retrieve the clan name of a clan wars server member from the cache."""
    member_info = clan_wars_server_members_cache.get(user_id)
    if member_info:
        return member_info.get("clan_name")
    return None

def remove_member_from_cache(user_id: int):
    """Remove a clan wars server member from the cache."""
    if user_id in clan_wars_server_members_cache:
        removed_member = clan_wars_server_members_cache.pop(user_id)
        pretty_log(
            tag="cache",
            message=f"Removed clan wars server member from cache: {removed_member['user_name']} ({user_id})",
        )
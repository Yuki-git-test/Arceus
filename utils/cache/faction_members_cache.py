import discord

from utils.cache.cache_list import faction_members_cache
from utils.db.faction_members import fetch_faction_members
from utils.logs.pretty_log import pretty_log

# Structure:
# faction_members_cache = {
# user_id:{
# "clan_name": str,
# "faction": str,
# "notify": str
# },

# 🌸──────────────────────────────────────────────
#      🛡️ Faction Members Cache Functions
# 🌸──────────────────────────────────────────────
async def load_faction_members_cache(bot: discord.Client):
    """Load the faction members cache from the database."""
    faction_members_cache.clear()
    try:
        members = await fetch_faction_members(bot=bot)
        if not members:
            pretty_log(
                message="⚠️ No faction members found to load into cache.",
                tag="cache",
            )
            return

        for member in members:
            user_id = member["user_id"]
            faction_members_cache[user_id] = {
                "user_name": member["user_name"],
                "clan_name": member["clan_name"],
                "faction": member["faction"],
                "notify": member["notify"],
            }

        pretty_log(
            message=f"✅ Loaded {len(faction_members_cache)} faction members into cache.",
            tag="cache",
        )

        if len(faction_members_cache) == 0:
            pretty_log(
                message="⚠️ Faction members cache is empty after loading.",
                tag="cache",
            )
        return faction_members_cache

    except Exception as e:
        pretty_log(
            message=f"❌ Error loading faction members cache: {e}",
            tag="cache",
        )
        raise e

def upsert_faction_member_into_cache(
    user_id: int,
    user_name: str,
    clan_name: str,
    faction: str,
    notify: str,
):
    """Upsert a faction member into the cache."""
    faction_members_cache[user_id] = {
        "user_name": user_name,
        "clan_name": clan_name,
        "faction": faction,
        "notify": notify,
    }
    pretty_log(
        message=f"✅ Upserted faction member into cache with user ID: {user_id}",
        tag="cache",
    )

def update_faction_member_notify_in_cache(
    user_id: int,
    notify: str,
):
    """Update the notify preference for a faction member in the cache."""
    if user_id in faction_members_cache:
        faction_members_cache[user_id]["notify"] = notify
        user_name = faction_members_cache[user_id].get("user_name", "Unknown")
        pretty_log(
            message=f"✅ Updated notify preference in cache for faction member {user_name} to {notify}",
            tag="cache",
        )


def update_faction_member_faction_in_cache(
    user_id: int,
    faction: str,
):
    """Update the faction for a faction member in the cache."""
    if user_id in faction_members_cache:
        faction_members_cache[user_id]["faction"] = faction
        user_name = faction_members_cache[user_id].get("user_name", "Unknown")
        pretty_log(
            message=f"✅ Updated faction in cache for faction member {user_name} to {faction}",
            tag="cache",
        )


def remove_faction_member_from_cache(user_id: int):
    """Remove a faction member from the cache."""
    if user_id in faction_members_cache:
        user_name = faction_members_cache[user_id].get("user_name", "Unknown")
        del faction_members_cache[user_id]
        pretty_log(
            message=f"✅ Removed faction member {user_name} from cache with user ID: {user_id}",
            tag="cache",
        )

def fetch_faction_member_id_by_username(user_name: str) -> int | None:
    """Fetch a faction member's user_id by their user_name from the cache."""
    for user_id, data in faction_members_cache.items():
        if data.get("user_name") == user_name:
            return user_id
    return None
import discord
from utils.cache.cache_list import active_wb_cache
from utils.logs.pretty_log import pretty_log
from utils.db.active_wb_db import fetch_active_wb

async def load_active_wb_cache(bot: discord.Client):
    active_wb_cache.clear()
    try:
        row = await fetch_active_wb(bot)
        if row:
            active_wb_cache["wb_timestamp"] = {
                "boss_name": row["boss_name"],
                "wb_timestamp": row["wb_timestamp"],
            }
    except Exception as e:
        pretty_log(f"Error loading active world boss cache: {e}")

def upsert_active_wb_cache(boss_name: str, wb_timestamp: int):
    active_wb_cache.clear()
    active_wb_cache["wb_timestamp"] = {
        "boss_name": boss_name,
        "wb_timestamp": wb_timestamp,
    }

def remove_active_wb_cache():
    active_wb_cache.clear()

def fetch_active_wb_timestamp_and_boss():
    wb_data = active_wb_cache.get("wb_timestamp")
    if wb_data:
        return wb_data.get("wb_timestamp"), wb_data.get("boss_name")
    return None, None
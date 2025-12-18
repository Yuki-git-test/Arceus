from utils.logs.pretty_log import pretty_log

processed_fish_spawn_message_ids = set()
processed_faction_ball_alerts = set()
processed_pokemon_spawn_msgs = set()
processed_market_feed_message_ids = set()
processed_market_feed_ids = set()

def clear_processed_messages_cache():
    """Clears all processed message ID caches."""
    processed_fish_spawn_message_ids.clear()
    processed_pokemon_spawn_msgs.clear()
    processed_faction_ball_alerts.clear()
    processed_market_feed_message_ids.clear()
    processed_market_feed_ids.clear()

    pretty_log(message="✅ Cleared all processed message ID caches", tag="cache")


market_alert_cache: list[dict] = []
# Structure: {
#     "user_id": int,
#     "pokemon": str,
#     "dex": str,
#     "max_price": int,
#     "channel_id": int,
#     "role_id": int
# }

_market_alert_index: dict[tuple[str, int], dict] = (
    {}
)  # key = (pokemon.lower(), channel_id)
# Structure
# _market_alert_index = {
#     ("pikachu", 987654321): {
#         "user_id": 123456789,
#         "pokemon": "Pikachu",
#         "dex_number": 25,
#         "max_price": 5000,
#         "channel_id": 987654321,
#         "role_id": 192837465
#     },

webhook_url_cache: dict[tuple[int, int], dict[str, str]] = {}
#     ...
#
# }
# key = (bot_id, channel_id)
# Structure:
# webhook_url_cache = {
# (bot_id, channel_id): {
#     "url": "https://discord.com/api/webhooks/..."
#     "channel_name": "alerts-channel",
# },
#

faction_members_cache: dict[int, dict[str, str]] = {}
# Structure:
# faction_members_cache = {
# user_id:{
# "user_name": str,
# "clan_name": str,
# "faction": str,
# "notify": str
# },

# 🌸──────────────────────────────────────────────
# Daily Faction Ball Cache (Global)
# ───────────────────────────────────────────────
daily_faction_ball_cache: dict[str, str | None] = {}
# Structure:
# daily_faction_ball_cache = {
#     "aqua": "Some Value or None",
#     "flare": "Some Value or None",
#     "galactic": None,
#     "magma": "Some Value or None",
#     "plasma": None,
#     "rocket": "Some Value or None",
#     "skull": None,
#     "yell": "Some Value or None"
# }


vna_members_cache: dict[int, dict] = {}
# Structure
# user_id: {
# "user_name": str,
# "pokemeow_name": str,
# "channel_id": int,
# "perks": str,
# "faction": str,
# }

user_alerts_cache: dict[int, dict[str, dict[str, str]]] = {}
# Structure:
# {
#   user_id: {
#     alert_type: {
#       "user_name": str,
#       "notify": str
#     },
#     ...
#   },
#   ...
# }

timer_cache: dict[int, dict[str, str]] = {}
# Structure:
# {
#   user_id: {
#     "user_name": str,
#     "pokemon_setting": str,
#     "fish_setting": str,
#     "battle_setting": str
#   },
#   ...
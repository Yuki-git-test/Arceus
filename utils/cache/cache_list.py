from utils.logs.pretty_log import pretty_log

processed_fish_spawn_message_ids = set()
processed_faction_ball_alerts = set()
processed_pokemon_spawn_msgs = set()
processed_market_feed_message_ids = set()
processed_market_feed_ids = set()
processed_explore_messages = set()
processed_caught_messages = set()
processed_weekly_stats_messages = set()
processed_monthly_stats_messages = set()


def clear_processed_messages_cache():
    """Clears all processed message ID caches."""
    processed_fish_spawn_message_ids.clear()
    processed_pokemon_spawn_msgs.clear()
    processed_faction_ball_alerts.clear()
    processed_market_feed_message_ids.clear()
    processed_market_feed_ids.clear()
    processed_explore_messages.clear()
    processed_caught_messages.clear()
    processed_weekly_stats_messages.clear()
    processed_monthly_stats_messages.clear()

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

ping_message_id_cache: dict[str, int] = {}
# Structure:
# {
# type: message_id,
#   ...
# }

weekly_goal_cache: dict[int, dict] = {}
# Structure:
# user_id -> {
#   "user_name": str,
#   "pokemon_caught": int,
#   "fish_caught": int,
#   "battles_won": int,
#   "channel_id": int,
#   "weekly_requirement_mark": bool,
# }

monthly_goal_cache: dict[int, dict] = {}
# Structure:
# user_id -> {
#   "user_name": str,
#   "pokemon_caught": int,
#   "fish_caught": int,
#   "battles_won": int,
#   "channel_id": int,
#   "monthly_requirement_mark": bool,
# }

clan_wars_server_members_cache: dict[int, dict[str, str | None]] = {}
# Structure:
# user_id -> {
#   "user_name": str,
#   "clan_name": str or None
# }

snipe_ga_active = False
market_value_cache: dict[str, dict] = {}
# Structure:
# {
#   pokemon_name: {
#     "dex_number": int,
#     "rarity": str,
# 🧩────────────────────────────────────────────
#        ⚡ Pokémon List Cache
# 🧩────────────────────────────────────────────
pokemon_list_cache: dict[str, int] = {}
# Structure:
# pokemon_list_cache = {
#     "pokemon_name": "dex_number",
#     }
# 🔮────────────────────────────────────────────
#        ⚡ EV Tracker Cache
# 👻────────────────────────────────────────────
ev_tracker_cache: dict[int, dict] = {}
# user_id -> {"user_name": str, "pokemon": str, "dex_number": int, "evs": dict, "goals": dict}
# Structure
# {
#   user_id: {
#       "user_name": str,
#       "pokemon": str,
#       "dex_number": int,
#        "emoji_id": str,
#       "evs": {
#           "hp": int,
#           "atk": int,
#           "def": int,
#           "spa": int,
#           "spd": int,
#           "spe": int,
#       },
#       "goals": {
#           "hp": int,
#           "atk": int,
#           "def": int,
#           "spa": int,
#           "spd": int,
#           "spe": int,
#       },
#   }

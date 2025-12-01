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

webhook_url_cache: dict[tuple[int, int], str] = {}
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

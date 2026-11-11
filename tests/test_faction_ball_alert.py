import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from Constants.aesthetic import Emojis_Balls
from Constants.faction_data import FACTION_LOGO_EMOJIS
from utils.cache.cache_list import (
    daily_faction_ball_cache,
    faction_members_cache,
    processed_faction_ball_alerts,
    processed_fish_spawn_message_ids,
    processed_pokemon_spawn_msgs,
)
from utils.cache.daily_fa_ball_cache import update_daily_faction_ball_cache
from utils.db.daily_faction_ball import fetch_all_faction_balls
from utils.listener_func import fish_spawn_listener, pokemon_spawn_listener
from utils.listener_func.pokemon_spawn_listener import faction_ball_alert


class FactionBallAlertTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.saved_balls = daily_faction_ball_cache.copy()
        self.saved_members = faction_members_cache.copy()
        self.saved_processed = processed_faction_ball_alerts.copy()
        self.saved_fish = processed_fish_spawn_message_ids.copy()
        self.saved_spawns = processed_pokemon_spawn_msgs.copy()
        daily_faction_ball_cache.clear()
        faction_members_cache.clear()
        processed_faction_ball_alerts.clear()
        processed_fish_spawn_message_ids.clear()
        processed_pokemon_spawn_msgs.clear()
        self.addCleanup(self.restore_caches)
        logger = patch("utils.cache.daily_fa_ball_cache.pretty_log")
        logger.start()
        self.addCleanup(logger.stop)
        self.member = SimpleNamespace(id=1, name="trainer", mention="<@1>")
        faction_members_cache[1] = {"faction": "flare", "notify": "on_no_pings"}
        self.send = AsyncMock()
        self.message = SimpleNamespace(
            id=123,
            embeds=[SimpleNamespace(description=FACTION_LOGO_EMOJIS["flare"])],
            channel=SimpleNamespace(send=self.send),
        )

    def restore_caches(self):
        daily_faction_ball_cache.clear()
        daily_faction_ball_cache.update(self.saved_balls)
        faction_members_cache.clear()
        faction_members_cache.update(self.saved_members)
        processed_faction_ball_alerts.clear()
        processed_faction_ball_alerts.update(self.saved_processed)
        processed_fish_spawn_message_ids.clear()
        processed_fish_spawn_message_ids.update(self.saved_fish)
        processed_pokemon_spawn_msgs.clear()
        processed_pokemon_spawn_msgs.update(self.saved_spawns)

    async def test_missing_cached_ball_is_loaded_from_database(self):
        daily_faction_ball_cache["flare"] = None
        with patch(
            "utils.cache.daily_fa_ball_cache.fetch_all_faction_balls",
            new_callable=AsyncMock,
            return_value={"flare": "masterball"},
        ) as fetch:
            await faction_ball_alert(object(), self.member, self.message, self.message)
        fetch.assert_awaited_once()
        self.assertEqual(daily_faction_ball_cache["flare"], "masterball")
        self.send.assert_awaited_once()
        content = self.send.await_args.args[0]
        self.assertIn(Emojis_Balls.masterball, content)
        self.assertNotIn("<@1>", content)

    async def test_missing_ball_in_database_still_prompts_for_faction(self):
        with patch(
            "utils.cache.daily_fa_ball_cache.fetch_all_faction_balls",
            new_callable=AsyncMock,
            return_value={"flare": None},
        ):
            await faction_ball_alert(object(), self.member, self.message, self.message)
        self.assertIn("daily ball yet", self.send.await_args.args[0])

    async def test_cached_ball_does_not_query_database(self):
        daily_faction_ball_cache["flare"] = "masterball"
        with patch(
            "utils.cache.daily_fa_ball_cache.fetch_all_faction_balls",
            new_callable=AsyncMock,
        ) as fetch:
            await faction_ball_alert(object(), self.member, self.message, self.message)
        fetch.assert_not_awaited()
        self.assertIn(Emojis_Balls.masterball, self.send.await_args.args[0])

    async def test_database_failure_does_not_report_unknown_ball(self):
        with patch(
            "utils.cache.daily_fa_ball_cache.fetch_all_faction_balls",
            new_callable=AsyncMock,
            side_effect=RuntimeError("database unavailable"),
        ):
            with self.assertRaisesRegex(RuntimeError, "database unavailable"):
                await faction_ball_alert(object(), self.member, self.message, self.message)
        self.send.assert_not_awaited()

    def test_valid_update_populates_empty_cache(self):
        update_daily_faction_ball_cache("flare", "masterball")
        self.assertEqual(daily_faction_ball_cache["flare"], "masterball")

    async def test_database_failure_is_logged_and_propagated(self):
        bot = SimpleNamespace(pg_pool=SimpleNamespace(acquire=lambda: None))
        with patch("utils.db.daily_faction_ball.pretty_log") as log:
            with self.assertRaises(TypeError):
                await fetch_all_faction_balls(bot)
        log.assert_called_once()

    async def test_spawn_listeners_refresh_and_use_saved_ball(self):
        for fishing in (False, True):
            with self.subTest(fishing=fishing):
                processed_faction_ball_alerts.clear()
                daily_faction_ball_cache.clear()
                verb = "fished" if fishing else "found"
                self.message.embeds[0].description = (
                    f"{FACTION_LOGO_EMOJIS['flare']} **trainer** {verb} a wild Pokemon"
                )
                self.message.content = "trainer found a wild Pokemon"
                self.message.guild = object()
                bot = object()
                module = fish_spawn_listener if fishing else pokemon_spawn_listener
                with (
                    patch.object(
                        module, "get_pokemeow_reply_member",
                        new_callable=AsyncMock, return_value=self.member,
                    ),
                    patch(
                        "utils.cache.daily_fa_ball_cache.fetch_all_faction_balls",
                        new_callable=AsyncMock, return_value={"flare": "masterball"},
                    ),
                ):
                    if fishing:
                        await module.fish_spawn_listener(bot, self.message, self.message)
                    else:
                        await module.pokemon_spawn_listener(bot, self.message)
                self.assertIn(Emojis_Balls.masterball, self.send.await_args.args[0])
                self.send.reset_mock()


if __name__ == "__main__":
    unittest.main()

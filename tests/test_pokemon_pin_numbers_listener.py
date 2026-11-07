import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from utils.listener_func import pokemon_pin_numbers_listener as pin_listener


class PinNumbersListenerTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.member = SimpleNamespace(
            id=123, name="Trainer", mention="<@123>", avatar=None
        )
        self.channel = SimpleNamespace(id=456, name="safari", send=AsyncMock())
        self.message = SimpleNamespace(id=789, channel=self.channel)
        pin_listener.processed_pin_numbers_messages.discard(self.message.id)

        self.patches = [
            patch.object(
                pin_listener,
                "get_pokemeow_reply_or_interaction_member",
                new_callable=AsyncMock,
                return_value=self.member,
            ),
            patch.object(
                pin_listener,
                "fetch_user_alert_notify",
                new_callable=AsyncMock,
                return_value="on_no_pings",
            ),
            patch.object(pin_listener, "fetch_pin_number_type", new_callable=AsyncMock),
            patch.object(pin_listener, "upsert_pin_number_type", new_callable=AsyncMock),
            patch.object(pin_listener, "fetch_all_pin_numbers", new_callable=AsyncMock),
            patch.object(pin_listener, "_retry_discord_call", new_callable=AsyncMock),
            patch.object(pin_listener, "debug_log"),
        ]
        self.mocks = []
        for patcher in self.patches:
            self.mocks.append(patcher.start())
            self.addCleanup(patcher.stop)
        self.addCleanup(pin_listener.processed_pin_numbers_messages.discard, self.message.id)

    async def run_listener(self, current, saved, pin="3"):
        self.mocks[2].return_value = current
        self.mocks[4].return_value = saved
        await pin_listener.pokemon_pin_numbers_listener(
            bot=object(), message=self.message, pin_number=pin, source="safari"
        )

    async def test_unchanged_pin_does_not_send_summary(self):
        await self.run_listener(3, None)

        self.mocks[5].assert_awaited_once()
        self.mocks[3].assert_not_awaited()
        self.mocks[4].assert_not_awaited()
        self.channel.send.assert_not_awaited()

    async def test_new_pin_sends_summary_without_completion(self):
        await self.run_listener(None, {"pokemon_pin": "1", "fish_pin": None, "sz_pin": "3"})

        self.mocks[3].assert_awaited_once()
        self.channel.send.assert_awaited_once()
        self.assertNotIn("all pin numbers", self.channel.send.await_args.kwargs.get("content", "").lower())

    async def test_last_missing_pin_announces_completion(self):
        await self.run_listener(None, {"pokemon_pin": "1", "fish_pin": "2", "sz_pin": "3"})

        self.channel.send.assert_awaited_once()
        self.assertIn("all pin numbers", self.channel.send.await_args.kwargs["content"].lower())

    async def test_changed_pin_sends_summary_without_reannouncing_completion(self):
        await self.run_listener("4", {"pokemon_pin": "1", "fish_pin": "2", "sz_pin": "3"})

        self.mocks[3].assert_awaited_once()
        self.channel.send.assert_awaited_once()
        self.assertNotIn("all pin numbers", self.channel.send.await_args.kwargs.get("content", "").lower())

    async def test_zero_pin_is_discovered(self):
        await self.run_listener(None, {"pokemon_pin": 0, "fish_pin": "2", "sz_pin": "3"})

        self.assertIn("all pin numbers", self.channel.send.await_args.kwargs["content"].lower())


if __name__ == "__main__":
    unittest.main()

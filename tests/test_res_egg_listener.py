import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import discord

from utils.functions.message_link import get_jump_to_message_link
from utils.listener_func import res_egg_listener


class MessageLinkTests(unittest.TestCase):
    def test_guild_message_link(self):
        message = SimpleNamespace(
            guild=SimpleNamespace(id=123), channel=SimpleNamespace(id=456), id=789
        )
        self.assertEqual(
            get_jump_to_message_link(message),
            "[Jump to message](https://discord.com/channels/123/456/789)",
        )

    def test_direct_message_link(self):
        message = SimpleNamespace(guild=None, channel=SimpleNamespace(id=456), id=789)
        self.assertEqual(
            get_jump_to_message_link(message),
            "[Jump to message](https://discord.com/channels/@me/456/789)",
        )


class ResearchEggListenerTests(unittest.IsolatedAsyncioTestCase):
    async def test_announcement_links_to_hatch_message(self):
        source_embed = discord.Embed(
            description="**Purple Egg** hatched in **Lab Incubator 1**! **Zorua**"
        )
        source_embed.set_author(name="Trainer's Research Lab Hatch")
        guild = SimpleNamespace(id=123, name="Test server", icon=None)
        message = SimpleNamespace(
            guild=guild,
            channel=SimpleNamespace(id=456),
            id=789,
            jump_url="https://discord.com/channels/123/456/789",
            embeds=[source_embed],
        )
        destination = object()
        with (
            patch.object(res_egg_listener, "get_rarespawn_channel", return_value=destination),
            patch.object(res_egg_listener, "get_dex_number_by_name", return_value=570),
            patch.object(res_egg_listener, "get_mon_value", new_callable=AsyncMock, return_value=None),
            patch.object(res_egg_listener, "send_webhook", new_callable=AsyncMock) as send,
        ):
            await res_egg_listener.handle_res_egg_hatch(bot=object(), message=message)

        send.assert_awaited_once()
        announcement = send.await_args.kwargs["embed"]
        self.assertEqual(announcement.url, message.jump_url)
        self.assertIn(
            "[Jump to message](https://discord.com/channels/123/456/789)",
            announcement.description,
        )
        self.assertIn("Zorua #570", announcement.description)


if __name__ == "__main__":
    unittest.main()

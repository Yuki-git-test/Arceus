import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import discord

from Constants.aesthetic import Emojis_Balls
from utils.essentials.ball_names import normalize_ball_type
from utils.essentials.balls_to_bring import build_balls_to_bring_embed
from utils.listener_func import catchlist_cl_compact_listener, catchlist_cl_listener


class BallsToBringTests(unittest.TestCase):
    def test_accented_pokeball_normalizes(self):
        self.assertEqual(normalize_ball_type("Poké Ball"), "pokeball")

    def test_embed_has_emoji_only_fields_in_ball_order_and_skips_safari(self):
        embed = build_balls_to_bring_embed(
            [
                {"catch_type": ";p", "ball_type": "lureball", "completion": False},
                {"catch_type": ";p", "ball_type": "greatball", "completion": False},
                {"catch_type": ";p", "ball_type": "poké ball", "completion": False},
                {"catch_type": ";p", "ball_type": "pokeball", "completion": False},
                {"catch_type": ";fish", "ball_type": "lureball", "completion": False},
                {"catch_type": ";safarizone", "ball_type": "safariball", "completion": False},
            ]
        )
        self.assertEqual(embed.title, "Balls to Bring")
        self.assertEqual([f.name for f in embed.fields], [";p", ";f"])
        self.assertEqual(
            embed.fields[0].value,
            f"{Emojis_Balls.pokeball} {Emojis_Balls.greatball} {Emojis_Balls.Lure_Ball}",
        )
        self.assertEqual(embed.fields[1].value, Emojis_Balls.Lure_Ball)

    def test_each_command_uses_its_own_ball_order(self):
        balls = ["lureball", "diveball", "masterball", "duskball", "quickball"]
        embed = build_balls_to_bring_embed(
            [
                {"catch_type": c, "ball_type": b, "completion": False}
                for c in (";p", ";fish") for b in balls
            ]
        )
        self.assertEqual(
            embed.fields[0].value,
            " ".join(
                [
                    Emojis_Balls.masterball,
                    Emojis_Balls.Dusk_Ball,
                    Emojis_Balls.Quick_Ball,
                    Emojis_Balls.Dive_Ball,
                    Emojis_Balls.Lure_Ball,
                ]
            ),
        )
        self.assertEqual(
            embed.fields[1].value,
            " ".join(
                [
                    Emojis_Balls.Dive_Ball,
                    Emojis_Balls.masterball,
                    Emojis_Balls.Lure_Ball,
                    Emojis_Balls.Dusk_Ball,
                    Emojis_Balls.Quick_Ball,
                ]
            ),
        )

    def test_no_embed_when_only_safari(self):
        self.assertIsNone(
            build_balls_to_bring_embed(
                [{"catch_type": ";safarizone", "ball_type": "safariball", "completion": False}]
            )
        )

    def test_completed_entries_do_not_contribute_balls(self):
        embed = build_balls_to_bring_embed(
            [
                {"catch_type": ";p", "ball_type": "heavyball", "completion": True},
                {"catch_type": ";p", "ball_type": "greatball", "completion": True},
                {"catch_type": ";p", "ball_type": "greatball", "completion": False},
                {"catch_type": ";fish", "ball_type": "heavyball", "completion": False},
                {"catch_type": ";fish", "ball_type": "lureball", "completion": True},
            ]
        )
        self.assertEqual([(field.name, field.value) for field in embed.fields], [
            (";p", Emojis_Balls.greatball),
            (";f", Emojis_Balls.Heavy_Ball),
        ])

    def test_no_embed_when_all_pokemon_are_complete(self):
        self.assertIsNone(build_balls_to_bring_embed([
            {"catch_type": ";p", "ball_type": "heavyball", "completion": True},
            {"catch_type": ";fish", "ball_type": "lureball", "completion": True},
        ]))

    def test_command_with_only_completed_pokemon_has_no_field(self):
        embed = build_balls_to_bring_embed([
            {"catch_type": ";p", "ball_type": "heavyball", "completion": True},
            {"catch_type": ";fish", "ball_type": "lureball", "completion": False},
        ])
        self.assertEqual([(field.name, field.value) for field in embed.fields], [
            (";f", Emojis_Balls.Lure_Ball),
        ])


class CatchlistListenerBallsTests(unittest.IsolatedAsyncioTestCase):
    async def run_listener(self, compact, all_complete):
        module = catchlist_cl_compact_listener if compact else catchlist_cl_listener
        member = SimpleNamespace(id=1, name="tester", display_name="tester")
        rows = [
            ("✅", "Pikachu", "Heavy Ball", ";p"),
            ("✅" if all_complete else "⬜", "Eevee", "Great Ball", ";p"),
            ("✅" if all_complete else "⬜", "Magikarp", "Lure Ball", ";fish"),
        ]
        embed = discord.Embed(title="tester's catchlist - November", description=(
            "Catch the listed Pokémon" if compact
            else "Catch the listed Pokémon with its required ball"
        ))
        if compact:
            embed.description += "\n" + "\n".join(
                f"{status} <:mon:1> {name} · <:ball:2> **{ball}** · "
                f"<:command:3> `{command}` · 10 EXP"
                for status, name, ball, command in rows
            )
        else:
            for status, name, ball, command in rows:
                embed.add_field(
                    name=name,
                    value=f"{status} <:mon:1> {name} from <:command:3> `{command}`\n"
                    f"<:ball:2> **{ball}** · 10 EXP",
                )
        embed.set_footer(text="Activity (All) · Page 1/1")
        send = AsyncMock()
        message = SimpleNamespace(id=123, embeds=[embed], channel=SimpleNamespace(send=send))
        self.addCleanup(module._catchlist_pages.pop, message.id, None)
        listener = module.parse_catchlist_cl_compact if compact else module.parse_catchlist_cl_noncompact
        with (
            patch.object(module, "get_pokemeow_reply_or_interaction_member", new_callable=AsyncMock, return_value=member),
            patch.object(module, "upsert_catchlist", new_callable=AsyncMock) as save,
            patch.object(module, "pretty_log"),
            patch("utils.cache.user_alert_cache.fetch_user_alert_notify_cache", return_value=True),
        ):
            result = await listener(object(), message)
        self.assertEqual([mon["completion"] for mon in result["catch_list_mons"]],
                         [True, all_complete, all_complete])
        self.assertEqual(save.await_args.kwargs["catchlist_mons"], result["catch_list_mons"])
        send.assert_awaited_once()
        return send.await_args.kwargs

    async def test_both_listeners_exclude_completed_pokemon(self):
        for compact in (True, False):
            with self.subTest(compact=compact):
                kwargs = await self.run_listener(compact, all_complete=False)
                self.assertEqual([(field.name, field.value) for field in kwargs["embed"].fields], [
                    (";p", Emojis_Balls.greatball),
                    (";f", Emojis_Balls.Lure_Ball),
                ])

    async def test_both_listeners_omit_embed_when_all_complete(self):
        for compact in (True, False):
            with self.subTest(compact=compact):
                kwargs = await self.run_listener(compact, all_complete=True)
                self.assertNotIn("embed", kwargs)


if __name__ == "__main__":
    unittest.main()

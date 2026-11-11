import unittest

from Constants.aesthetic import Emojis_Balls
from utils.essentials.ball_names import normalize_ball_type
from utils.essentials.balls_to_bring import build_balls_to_bring_embed


class BallsToBringTests(unittest.TestCase):
    def test_accented_pokeball_normalizes(self):
        self.assertEqual(normalize_ball_type("Poké Ball"), "pokeball")

    def test_embed_has_emoji_only_fields_in_ball_order_and_skips_safari(self):
        embed = build_balls_to_bring_embed(
            [
                {"catch_type": ";p", "ball_type": "lureball"},
                {"catch_type": ";p", "ball_type": "greatball"},
                {"catch_type": ";p", "ball_type": "poké ball"},
                {"catch_type": ";p", "ball_type": "pokeball"},
                {"catch_type": ";fish", "ball_type": "lureball"},
                {"catch_type": ";safarizone", "ball_type": "safariball"},
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
            [{"catch_type": c, "ball_type": b} for c in (";p", ";fish") for b in balls]
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
                [{"catch_type": ";safarizone", "ball_type": "safariball"}]
            )
        )


if __name__ == "__main__":
    unittest.main()

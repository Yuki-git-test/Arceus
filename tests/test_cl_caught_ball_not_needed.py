import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from utils.cache.cache_list import (
    catchlist_cache,
    processed_caught_catchlist_messages,
)
from utils.db.catchlist_db import CatchlistCatchResult
from utils.listener_func import cl_caught


def mon(name, ball, catch_type=";p", done=False):
    return {
        "pokemon_name": name,
        "ball_type": ball,
        "catch_type": catch_type,
        "exp_amount": 10,
        "completion": done,
    }


class BallNoLongerNeededTests(unittest.IsolatedAsyncioTestCase):
    async def run_catch(self, ball, mons, catch_type_color=None):
        member = SimpleNamespace(id=1, mention="<@1>")
        catchlist_cache[1] = {"catchlist_mons": mons}
        self.addCleanup(catchlist_cache.pop, 1, None)

        async def fake_apply(bot, user_id, name, catch_type, ball_used):
            for m in mons:
                if m["pokemon_name"] == name and m["catch_type"] == catch_type:
                    m["completion"] = True
            return CatchlistCatchResult(False, False, 5)

        embed = SimpleNamespace(
            description=f"**Pikachu** with a <:b:1> {ball.title()}!",
            color=SimpleNamespace(value=catch_type_color) if catch_type_color else None,
        )
        send = AsyncMock()
        message = SimpleNamespace(
            id=555, embeds=[embed], channel=SimpleNamespace(send=send)
        )
        self.addCleanup(processed_caught_catchlist_messages.discard, 555)
        with (
            patch.object(
                cl_caught,
                "get_pokemeow_reply_or_interaction_member",
                new_callable=AsyncMock,
                return_value=member,
            ),
            patch.object(cl_caught, "apply_catchlist_catch", side_effect=fake_apply),
        ):
            await cl_caught.catchlist_caught_listener(object(), message, message)
        return send

    async def test_tells_user_when_last_non_default_ball_is_used(self):
        send = await self.run_catch("heavyball", [mon("pikachu", "heavyball")])
        send.assert_awaited_once()
        text = send.await_args.args[0]
        self.assertIn("`;p`", text)
        self.assertIn("Heavy Ball", text)

    async def test_silent_when_ball_still_needed(self):
        send = await self.run_catch(
            "heavyball", [mon("pikachu", "heavyball"), mon("eevee", "heavyball")]
        )
        send.assert_not_awaited()

    async def test_silent_for_default_ball(self):
        send = await self.run_catch("greatball", [mon("pikachu", "greatball")])
        send.assert_not_awaited()

    async def test_other_command_needing_ball_does_not_block_message(self):
        send = await self.run_catch(
            "heavyball",
            [mon("pikachu", "heavyball"), mon("eevee", "heavyball", ";fish")],
        )
        send.assert_awaited_once()


if __name__ == "__main__":
    unittest.main()

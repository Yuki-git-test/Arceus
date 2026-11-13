import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import discord

from Constants.vn_allstars_constants import VN_ALLSTARS_ROLES
from utils.cache.cache_list import daily_faction_ball_cache, faction_members_cache
from utils.db.faction_members import update_faction_member_notify
from utils.group_command_func.toggle import alerts
from utils.listener_func.faction_ball_listener import extract_faction_ball_from_fa


class FactionAlertSettingsTests(unittest.IsolatedAsyncioTestCase):
    async def open_settings(self, roles, existing=None):
        role_ids = (
            VN_ALLSTARS_ROLES.vna_member,
            VN_ALLSTARS_ROLES.wsg_members,
            VN_ALLSTARS_ROLES.seafoam,
        )
        role_objects = {role_id: object() for role_id in role_ids}
        user = SimpleNamespace(
            id=1, name="trainer", display_name="Trainer",
            roles=[role_objects[role_ids[index]] for index in roles],
        )
        interaction = SimpleNamespace(
            user=user,
            guild=SimpleNamespace(get_role=role_objects.get),
            response=SimpleNamespace(defer=AsyncMock()),
            followup=SimpleNamespace(send=AsyncMock(return_value=object())),
        )
        saved = existing

        async def fetch(bot, user_id):
            return saved

        async def upsert(**kwargs):
            nonlocal saved
            saved = {key: value for key, value in kwargs.items() if key != "bot"}

        with (
            patch.object(alerts, "fetch_faction_member", side_effect=fetch),
            patch.object(alerts, "upsert_faction_member", side_effect=upsert) as save,
            patch.object(alerts, "fetch_user_alert_notify", new_callable=AsyncMock, return_value=None),
            patch.object(alerts, "pretty_log"),
        ):
            await alerts.alert_settings_func(object(), interaction)
        view = interaction.followup.send.await_args.kwargs["view"]
        return user, view, save

    async def test_button_visible_and_usable_without_roles(self):
        user, view, save = await self.open_settings([])
        self.assertIn(view.faction_ball_alert_button, view.children)
        self.assertEqual(save.await_args.kwargs["clan_name"], "Other")
        self.assertIsNone(view.faction_member["faction"])
        interaction = SimpleNamespace(
            user=user,
            response=SimpleNamespace(defer=AsyncMock()),
            edit_original_response=AsyncMock(),
            followup=SimpleNamespace(send=AsyncMock()),
        )
        with (
            patch.object(alerts, "update_faction_member_notify", new_callable=AsyncMock) as update,
            patch.object(alerts, "pretty_log"),
        ):
            for expected in ("on", "on_no_pings", "react", "off"):
                await view.faction_ball_alert_button.callback(interaction)
                self.assertEqual(view.faction_member["notify"], expected)
                self.assertEqual(update.await_args.kwargs["notify"], expected)
        self.assertEqual(interaction.edit_original_response.await_count, 4)
        interaction.followup.send.assert_not_awaited()

    async def test_existing_member_retains_saved_faction_and_preference(self):
        existing = {"clan_name": "VNA", "faction": "flare", "notify": "react"}
        _, view, save = await self.open_settings([], existing)
        save.assert_not_awaited()
        self.assertIs(view.faction_member, existing)
        self.assertEqual(view.faction_ball_alert_button.label, "Faction Ball Alert: REACT")

    async def test_member_roles_keep_existing_clan_names(self):
        for index, name in enumerate(("VNA", "WSG", "Straymons")):
            with self.subTest(clan=name):
                _, view, save = await self.open_settings([index])
                self.assertIn(view.faction_ball_alert_button, view.children)
                self.assertEqual(save.await_args.kwargs["clan_name"], name)

    async def test_fa_updates_new_member_faction(self):
        previous = faction_members_cache.get(1)
        faction_members_cache[1] = {
            "clan_name": "Other", "user_name": "trainer",
            "faction": None, "notify": "on",
        }
        if previous is None:
            self.addCleanup(faction_members_cache.pop, 1, None)
        else:
            self.addCleanup(faction_members_cache.__setitem__, 1, previous)
        embed = discord.Embed(
            description="<:masterball:123> **Today's target Pokemon are**"
        )
        embed.set_author(name="Team Flare — Headquarters")
        message = SimpleNamespace(embeds=[embed])
        member = SimpleNamespace(id=1)
        with (
            patch("utils.listener_func.faction_ball_listener.get_pokemeow_reply_member",
                  new_callable=AsyncMock, return_value=member),
            patch("utils.listener_func.faction_ball_listener.update_faction_ball",
                  new_callable=AsyncMock),
            patch("utils.listener_func.faction_ball_listener.update_faction_member_faction",
                  new_callable=AsyncMock) as update,
        ):
            bot = object()
            await extract_faction_ball_from_fa(bot, message)
        update.assert_awaited_once_with(bot, 1, "flare")

    async def test_fa_updates_changed_cached_ball(self):
        had_previous_ball = "flare" in daily_faction_ball_cache
        previous_ball = daily_faction_ball_cache.get("flare")
        daily_faction_ball_cache["flare"] = "pokeball"

        def restore_ball():
            if had_previous_ball:
                daily_faction_ball_cache["flare"] = previous_ball
            else:
                daily_faction_ball_cache.pop("flare", None)

        self.addCleanup(restore_ball)
        embed = discord.Embed(description="<:masterball:123> **Today's target Pokemon are**")
        embed.set_author(name="Team Flare — Headquarters")
        message = SimpleNamespace(embeds=[embed])
        bot = object()
        with (
            patch(
                "utils.listener_func.faction_ball_listener.get_pokemeow_reply_member",
                new_callable=AsyncMock,
                return_value=None,
            ),
            patch(
                "utils.listener_func.faction_ball_listener.update_faction_ball",
                new_callable=AsyncMock,
            ) as update,
        ):
            await extract_faction_ball_from_fa(bot, message)

        update.assert_awaited_once_with(bot, "flare", "masterball")

    async def test_missing_database_row_does_not_report_success(self):
        connection = SimpleNamespace(execute=AsyncMock(return_value="UPDATE 0"))
        context = AsyncMock()
        context.__aenter__.return_value = connection
        bot = SimpleNamespace(pg_pool=SimpleNamespace(acquire=lambda: context))
        with patch("utils.db.faction_members.pretty_log") as log:
            with self.assertRaisesRegex(ValueError, "No faction member"):
                await update_faction_member_notify(bot, 1, "on")
        log.assert_called_once()

    async def test_new_user_persists_toggle_and_updates_cache(self):
        rows = {}

        class Connection:
            async def fetchrow(self, query, user_id):
                return rows.get(user_id)

            async def execute(self, query, *args):
                if "INSERT INTO faction_members" in query:
                    clan, user_id, user_name, faction, notify = args
                    rows[user_id] = {
                        "clan_name": clan, "user_id": user_id, "user_name": user_name,
                        "faction": faction, "notify": notify,
                    }
                    return "INSERT 0 1"
                if "SET notify" in query:
                    notify, user_id = args
                    rows[user_id]["notify"] = notify
                    return "UPDATE 1"
                raise AssertionError(f"Unexpected query: {query}")

        context = AsyncMock()
        context.__aenter__.return_value = Connection()
        bot = SimpleNamespace(pg_pool=SimpleNamespace(acquire=lambda: context))
        user = SimpleNamespace(id=12, name="trainer", display_name="Trainer", roles=[])
        interaction = SimpleNamespace(
            user=user,
            guild=SimpleNamespace(get_role=lambda role_id: None),
            response=SimpleNamespace(defer=AsyncMock()),
            followup=SimpleNamespace(send=AsyncMock(return_value=object())),
            edit_original_response=AsyncMock(),
        )
        previous = faction_members_cache.get(user.id)
        if previous is None:
            self.addCleanup(faction_members_cache.pop, user.id, None)
        else:
            self.addCleanup(faction_members_cache.__setitem__, user.id, previous)
        with (
            patch.object(alerts, "fetch_user_alert_notify", new_callable=AsyncMock, return_value=None),
            patch.object(alerts, "pretty_log"),
            patch("utils.db.faction_members.pretty_log"),
            patch("utils.cache.faction_members_cache.pretty_log"),
        ):
            await alerts.alert_settings_func(bot, interaction)
            view = interaction.followup.send.await_args.kwargs["view"]
            await view.faction_ball_alert_button.callback(interaction)
        self.assertEqual(rows[user.id]["clan_name"], "Other")
        self.assertEqual(rows[user.id]["notify"], "on")
        self.assertEqual(faction_members_cache[user.id]["notify"], "on")
        self.assertIsNone(rows[user.id]["faction"])


if __name__ == "__main__":
    unittest.main()

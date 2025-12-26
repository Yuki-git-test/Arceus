import discord
from discord import ButtonStyle
from discord.ext import commands

from Constants.vn_allstars_constants import VN_ALLSTARS_ROLES
from utils.cache.cache_list import vna_members_cache
from utils.db.faction_members import (
    fetch_faction_member,
    update_faction_member_notify,
    upsert_faction_member,
)
from utils.db.user_alerts_db import fetch_user_alert_notify, upsert_user_alert
from utils.logs.pretty_log import pretty_log


# 💗────────────────────────────────────────────
# [🎀 FUNCTION] Alert Settings
# 💗────────────────────────────────────────────
async def alert_settings_func(
    bot: commands.Bot,
    interaction: discord.Interaction,
):
    """Toggle alert settings for faction members."""
    user = interaction.user
    user_id = user.id
    user_name = user.name
    guild = interaction.guild

    # Get Roles
    vna_member_role = guild.get_role(VN_ALLSTARS_ROLES.vna_member)
    wsg_member_role = guild.get_role(VN_ALLSTARS_ROLES.wsg_members)
    seafoam_role = guild.get_role(VN_ALLSTARS_ROLES.seafoam)
    clan_name = None

    # Check if user has vna member role or wsg member role or seafoam role
    if not any(
        [
            vna_member_role in user.roles,
            wsg_member_role in user.roles,
            seafoam_role in user.roles,
        ]
    ):
        await interaction.response.send_message(
            "❌ You must be a member of either VNA or WSG clan to toggle alert settings.",
            ephemeral=True,
        )
        return

    faction_name = None
    if vna_member_role in user.roles:
        clan_name = "VNA"

        # Check if they are in cache
        vna_member = vna_members_cache.get(user_id)
        if vna_member:
            faction_name = vna_member.get("faction")
            if faction_name:
                faction_name = faction_name.lower()
            else:
                faction_name = None
    elif wsg_member_role in user.roles:
        clan_name = "WSG"
    elif seafoam_role in user.roles:
        clan_name = "Straymons"

    # Fetch faction member from DB
    try:
        faction_member = await fetch_faction_member(bot, user_id)
        if not faction_member:
            # Upsert to db
            await upsert_faction_member(
                bot=bot,
                clan_name=clan_name,
                user_id=user_id,
                user_name=user_name,
                faction=None,
                notify="off",
            )
            faction_member = await fetch_faction_member(bot, user_id)
        # Get WB Battle Alert Setting
        wb_battle_alert = await fetch_user_alert_notify(
            bot=bot,
            user_id=user_id,
            alert_type="wb_battle",
        )
        # Always wrap as dict for downstream usage
        if isinstance(wb_battle_alert, str):
            wb_battle_alert = {"notify": wb_battle_alert}
        elif not wb_battle_alert:
            wb_battle_alert = {"notify": "off"}

        view = Alert_Settings_View(
            bot=bot,
            user=user,
            faction_member=faction_member,
            wb_battle_alert=wb_battle_alert,
        )
        message = await interaction.response.send_message(
            content="Modify your Alert Settings:",
            view=view,
        )
        view.message = message
        pretty_log(
            tag="ui",
            message=f"{user_name} opened Alert Settings menu.",
            bot=bot,
        )
    except Exception as e:
        pretty_log(
            tag="error",
            message=f"Error fetching/upserting faction member for {user_name} ({user_id}): {e}",
            bot=bot,
        )
        await interaction.response.send_message(
            "❌ An error occurred while fetching your alert settings. Please try again later.",
            ephemeral=True,
        )
        return


# 💗────────────────────────────────────────────
# [🌸 VIEW CLASS] Alert Settings View (patched)
# 💗────────────────────────────────────────────
class Alert_Settings_View(discord.ui.View):

    def __init__(
        self, bot: commands.Bot, user: discord.Member, faction_member, wb_battle_alert
    ):
        super().__init__(timeout=180)
        self.bot = bot
        self.user = user
        self.faction_member = faction_member
        self.wb_battle_alert = wb_battle_alert
        self.message = None  # set later
        self.update_button_styles()

    # 💫────────────────────────────────────
    # [🎯 BUTTON] Faction Ball Alert (4-State Cycle)
    # 💫────────────────────────────────────
    @discord.ui.button(
        label="Faction Ball Alert: OFF", style=ButtonStyle.secondary, emoji="🎯"
    )
    async def faction_ball_alert_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        if interaction.user.id != self.user.id:
            await interaction.response.send_message(
                "❌ You cannot interact with this button.", ephemeral=True
            )
            return

        await interaction.response.defer()

        try:
            current_state = (
                str(self.faction_member.get("notify", "off")).lower()
                if self.faction_member
                else "off"
            )

            # 🔹 4-State Cycle: off → on → on_no_pings → react → off
            if current_state == "off":
                new_state = "on"
            elif current_state == "on":
                new_state = "on_no_pings"
            elif current_state == "on_no_pings":
                new_state = "react"
            else:  # react or any other state
                new_state = "off"

            await update_faction_member_notify(
                bot=self.bot,
                user_id=self.user.id,
                notify=new_state,
            )
            self.faction_member["notify"] = new_state

            # 🔹 Refresh buttons
            self.update_button_styles()

            # 🔹 Display friendly text
            display_text = {
                "off": "Off",
                "on": "On",
                "on_no_pings": "On (No Pings)",
                "react": "React",
            }.get(new_state, "OFF")

            await interaction.edit_original_response(
                content=f"Modify your Alert Settings:\n🎯 Faction Ball Alert set to **{display_text}**",
                view=self,
            )

            pretty_log(
                tag="ui",
                message=f"{self.user.display_name} set Faction Ball Alert to {display_text}",
                bot=self.bot,
            )

        except Exception as e:
            pretty_log(
                tag="error",
                message=f"Error toggling faction ball alert for {self.user.name} ({self.user.id}): {e}",
                bot=self.bot,
            )
            await interaction.followup.send(
                "❌ An error occurred while toggling your faction ball alert. Please try again later.",
                ephemeral=True,
            )
            return

    # 💫────────────────────────────────────
    # [🎯 BUTTON] WB Battle Alert (2-State Cycle)
    # 💫────────────────────────────────────
    @discord.ui.button(
        label="World Boss Battle Alert: OFF",
        style=ButtonStyle.secondary,
        emoji="⚔️",
    )
    async def wb_battle_alert_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        if interaction.user.id != self.user.id:
            await interaction.response.send_message(
                "❌ You cannot interact with this button.", ephemeral=True
            )
            return

        await interaction.response.defer()

        try:
            current_state = (
                str(self.wb_battle_alert.get("notify", "off")).lower()
                if self.wb_battle_alert
                else "off"
            )

            # 🔹 2-State Cycle: off → on → off
            new_state = "on" if current_state == "off" else "off"

            await upsert_user_alert(
                bot=self.bot,
                user_id=self.user.id,
                alert_type="wb_battle",
                user_name=self.user.name,
                notify=new_state,
            )
            self.wb_battle_alert["notify"] = new_state

            # 🔹 Refresh buttons
            self.update_button_styles()

            # 🔹 Display friendly text
            display_text = {
                "off": "Off",
                "on": "On",
            }.get(new_state, "OFF")

            await interaction.edit_original_response(
                content=f"Modify your Alert Settings:\n⚔️ World Boss Battle Alert set to **{display_text}**",
                view=self,
            )

            pretty_log(
                tag="ui",
                message=f"{self.user.display_name} set World Boss Battle Alert to {display_text}",
                bot=self.bot,
            )

        except Exception as e:
            pretty_log(
                tag="error",
                message=f"Error toggling WB battle alert for {self.user.name} ({self.user.id}): {e}",
                bot=self.bot,
            )
            await interaction.followup.send(
                "❌ An error occurred while toggling your World Boss Battle alert. Please try again later.",
                ephemeral=True,
            )
            return

    # 💫────────────────────────────────────
    # [🎨 STYLE UPDATE FUNCTION]
    # 💫────────────────────────────────────
    def update_button_styles(self):

        # 🎯 Faction Ball Alert Button (4 states)
        faction_ball_alert_state = (
            str(self.faction_member.get("notify", "off")).lower()
            if self.faction_member
            else "off"
        )

        if faction_ball_alert_state == "off":
            self.faction_ball_alert_button.style = ButtonStyle.secondary
            self.faction_ball_alert_button.label = "Faction Ball Alert: OFF"
        elif faction_ball_alert_state == "on":
            self.faction_ball_alert_button.style = ButtonStyle.success
            self.faction_ball_alert_button.label = "Faction Ball Alert: ON"
        elif faction_ball_alert_state == "on_no_pings":
            self.faction_ball_alert_button.style = ButtonStyle.primary
            self.faction_ball_alert_button.label = "Faction Ball Alert: ON (No Pings)"
        elif faction_ball_alert_state == "react":
            self.faction_ball_alert_button.style = ButtonStyle.danger
            self.faction_ball_alert_button.label = "Faction Ball Alert: REACT"
        else:
            self.faction_ball_alert_button.style = ButtonStyle.secondary
            self.faction_ball_alert_button.label = "Faction Ball Alert: OFF"

        # ⚔️ WB Battle Alert Button (2 states)
        wb_battle_alert_state = (
            str(self.wb_battle_alert.get("notify", "off")).lower()
            if self.wb_battle_alert
            else "off"
        )
        if wb_battle_alert_state == "off":
            self.wb_battle_alert_button.style = ButtonStyle.secondary
            self.wb_battle_alert_button.label = "World Boss Battle Alert: OFF"
        elif wb_battle_alert_state == "on":
            self.wb_battle_alert_button.style = ButtonStyle.success
            self.wb_battle_alert_button.label = "World Boss Battle Alert: ON"
        else:
            self.wb_battle_alert_button.style = ButtonStyle.secondary
            self.wb_battle_alert_button.label = "World Boss Battle Alert: OFF"

    # 💫────────────────────────────────────
    # [⏰ TIMEOUT HANDLER]
    # 💫────────────────────────────────────
    async def on_timeout(self):
        for item in self.children:
            item.disabled = True
        try:
            if self.message:
                await self.message.edit(
                    content="⏰ Alert Settings timed out — reopen the menu to modify again.",
                    view=self,
                )
        except Exception:
            pass

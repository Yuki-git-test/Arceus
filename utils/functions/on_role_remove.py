from datetime import datetime

import discord
from discord.ext import commands

from Constants.vn_allstars_constants import (
    VN_ALLSTARS_ROLES,
    VN_ALLSTARS_TEXT_CHANNELS,
    VNA_SERVER_ID,
)
from utils.db.market_alert_db import remove_recent_market_alerts
from utils.db.market_alert_user import fetch_market_alert_user, set_max_alerts
from utils.group_command_func.markert_alert.add import determine_max_alerts
from utils.logs.pretty_log import pretty_log

LOG_CHANNEL_ID = VN_ALLSTARS_TEXT_CHANNELS.member_logs

SPECIAL_BOOSTER_ROLES = [
    VN_ALLSTARS_ROLES.server_booster,
    VN_ALLSTARS_ROLES.top_monthly_grinder,
    VN_ALLSTARS_ROLES.shiny_donator,
    VN_ALLSTARS_ROLES.legendary_donator,
    VN_ALLSTARS_ROLES.diamond_donator,
]


# 🍭──────────────────────────────
#   🎀 Event: On Role Remove
# 🍭──────────────────────────────
async def handle_role_remove(
    bot: discord.Client,
    member: discord.Member,
    role: discord.Role,
):
    """Handle role removal events."""
    role_id = role.id

    # ————————————————————————————————
    # 🩵 VNA Server Role Remove Logic
    # ————————————————————————————————

    # ————————————————————————————————
    # 🩵 VNA Member Special Role Removed
    # ————————————————————————————————
    if role_id in SPECIAL_BOOSTER_ROLES or role_id == VN_ALLSTARS_ROLES.staff:
        # Fetch user info from market_alert_users table
        user_info = await fetch_market_alert_user(bot, member.id)
        if user_info:
            old_max_alerts = user_info["max_alerts"]
            alerts_used = user_info["alerts_used"]
            new_max_alerts = determine_max_alerts(member)
            if new_max_alerts < old_max_alerts:
                await set_max_alerts(bot, member.id, new_max_alerts)
                pretty_log(
                    message=(
                        f"Updated max alerts for member '{member.display_name}' "
                        f"from {old_max_alerts} to {new_max_alerts} due to role removal."
                    ),
                    tag="info",
                    label="Role Remove Event",
                )
                # Dm member about decreased max alerts
                alert_difference = old_max_alerts - new_max_alerts
                removed_alerts = []
                if alerts_used > new_max_alerts:
                    # Remove most recent alerts to fit new max_alerts
                    num_alerts_to_remove = alerts_used - new_max_alerts
                    removed_alerts = await remove_recent_market_alerts(
                        bot, member, num_alerts_to_remove
                    )
                    pretty_log(
                        message=(
                            f"Removed {len(removed_alerts)} market alerts for member "
                            f"'{member.display_name}' due to decreased max alerts."
                        ),
                        tag="info",
                        label="Role Remove Event",
                    )
                try:
                    removed_alerts_line = ""
                    if removed_alerts:
                        removed_alerts_line = (
                            "\n**Removed Alerts:**\n" +
                            "\n".join(
                                [
                                    f"- {alert['pokemon']} (Dex: {alert['dex']}, Max Price: {alert['max_price']})"
                                    for alert in removed_alerts
                                ]
                            )
                        )
                    embed = discord.Embed(
                        title="📉 Market Alert Limit Decreased!",
                        description=(
                            f"**Old Max Alerts:** {old_max_alerts}\n"
                            f"**New Max Alerts:** {new_max_alerts}\n"
                            f"**Alerts Currently Used:** {alerts_used}\n"
                            f"{removed_alerts_line}"
                        ),
                        color=0xFF0000,
                    )
                    await member.send(
                        content=f"Your market alert limit has been decreased due to {role.name} role removal.",
                        embed=embed,
                    )
                except Exception as e:
                    pretty_log(
                        message=(
                            f"Failed to DM member '{member.display_name}' about decreased max alerts: {e}"
                        ),
                        tag="error",
                        label="Role Remove Event",
                    )

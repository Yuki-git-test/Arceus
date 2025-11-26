from datetime import datetime
import discord
from discord.ext import commands

from Constants.vn_allstars_constants import (
    VN_ALLSTARS_ROLES,
    VN_ALLSTARS_TEXT_CHANNELS,
    VNA_SERVER_ID,
)
from utils.logs.pretty_log import pretty_log
from utils.group_command_func.markert_alert.add import determine_max_alerts
from utils.db.market_alert_user import set_max_alerts, fetch_market_alert_user
LOG_CHANNEL_ID = VN_ALLSTARS_TEXT_CHANNELS.member_logs
SPECIAL_BOOSTER_ROLES = [
    VN_ALLSTARS_ROLES.server_booster,
    VN_ALLSTARS_ROLES.top_monthly_grinder,
    VN_ALLSTARS_ROLES.shiny_donator,
    VN_ALLSTARS_ROLES.legendary_donator,
    VN_ALLSTARS_ROLES.diamond_donator,
]

# 🍭──────────────────────────────
#   🎀 Event: On Role Add
# 🍭──────────────────────────────
async def handle_role_add(
    bot: discord.Client,
    member: discord.Member,
    role: discord.Role,
):
    """Handle role addition events."""
    role_id = role.id

    # ————————————————————————————————
    # 🩵 VNA Special Booster Role Add
    # ————————————————————————————————
    if role_id in SPECIAL_BOOSTER_ROLES or role_id == VN_ALLSTARS_ROLES.staff:
        # Fetch user info from market_alert_users table
        user_info = await fetch_market_alert_user(bot, member.id)
        if user_info:
            old_max_alerts = user_info["max_alerts"]
            alerts_used = user_info["alerts_used"]
            new_max_alerts = determine_max_alerts(member)
            if new_max_alerts > old_max_alerts:
                await set_max_alerts(bot, member.id, new_max_alerts)
                pretty_log(
                    message=(
                        f"Updated max alerts for member '{member.display_name}' "
                        f"from {old_max_alerts} to {new_max_alerts} due to role addition."
                    ),
                    tag="info",
                    label="Role Add Event",
                )
                # Dm member about increased max alerts
                try:
                    embed = discord.Embed(
                        title="📈 Market Alert Limit Increased!",
                        description=(
                            f"**Old Max Alerts:** {old_max_alerts}\n"
                            f"**New Max Alerts:** {new_max_alerts}\n"
                            f"**Alert Usage:** {alerts_used}/{new_max_alerts}\n"
                            f"**Reason:** You gained {role.name} role!"
                        ),
                        color=discord.Color.green(),
                        timestamp=datetime.now(),
                    )
                    embed.set_author(
                        name=member.display_name, icon_url=member.display_avatar.url
                    )
                    await member.send(embed=embed)
                except Exception as e:
                    pretty_log(
                        message=(
                            f"Failed to send DM to member '{member.display_name}' "
                            f"about increased max alerts: {e}"
                        ),
                        tag="error",
                        label="Role Add Event",
                    )





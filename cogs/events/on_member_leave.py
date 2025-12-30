from datetime import datetime

import discord
from discord.ext import commands

from Constants.vn_allstars_constants import (
    VN_ALLSTARS_ROLES,
    VN_ALLSTARS_TEXT_CHANNELS,
    VNA_EMBED_COLOR,
    VNA_SERVER_ID,
)
from utils.cache.cache_list import vna_members_cache
from utils.db.faction_members import remove_faction_member
from utils.db.market_alert_db import remove_all_market_alerts_for_user
from utils.db.market_alert_user import remove_market_alert_user
from utils.db.misc_pokemeow_reminders_db import remove_secret_santa_reminder
from utils.db.special_npc_timer_db_func import remove_special_battle_timer
from utils.db.timers_db import delete_timer
from utils.db.user_alerts_db import remove_user_alerts_for_user
from utils.db.vna_members_db_func import remove_member
from utils.functions.webhook_func import send_webhook
from utils.logs.pretty_log import pretty_log

LOG_CHANNEL_ID = VN_ALLSTARS_TEXT_CHANNELS.member_logs


GRAVEYARD_CATEGORY_ID = 1329157603573633126


async def db_cleanup_on_member_leave(bot, member: discord.Member):
    """Clean up database entries when a member leaves."""
    await remove_member(bot, member)
    await remove_faction_member(bot, member.id)
    await remove_all_market_alerts_for_user(bot, member.id)
    await remove_market_alert_user(bot, member.id)
    await remove_secret_santa_reminder(bot, member.id)
    await delete_timer(bot, member.id)
    await remove_user_alerts_for_user(bot, member.id)
    await remove_special_battle_timer(bot, member.id)

    pretty_log(
        message=f"Cleaned up database entries for member '{member.display_name}' ({member.id}) who left the server.",
        tag="info",
    )


# 🍭──────────────────────────────
#   🎀 Event: On Member Leave
# 🍭──────────────────────────────
class OnMemberLeaveCog(commands.Cog):
    """Cog to handle member leave events."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        """Handle member leave events."""
        # Only log leaves in VNA server
        guild = self.bot.get_guild(VNA_SERVER_ID)
        if guild is None:
            return

        if member.guild.id != VNA_SERVER_ID:
            return

        # 🍭──────────────────────────────
        #   🎀 Cleanup database entries
        # 🍭──────────────────────────────
        # Clean up other database entries
        await db_cleanup_on_member_leave(self.bot, member)


async def setup(bot: commands.Bot):
    await bot.add_cog(OnMemberLeaveCog(bot))

import asyncio

from discord.ext import commands

# 🧹 Import your scheduled tasks
from utils.background_task.reminders_checker import check_and_trigger_reminders
from utils.background_task.secret_santa_timer_checker import secret_santa_timer_checker
from utils.background_task.shiny_bonus_checker import (
    check_and_handle_expired_shiny_bonus,
)
from utils.background_task.special_battle_timer_checker import (
    special_battle_timer_checker,
)
from utils.logs.pretty_log import pretty_log


# 🍰──────────────────────────────
#   🎀 Cog: CentralLoop
#   Handles background tasks every 60 seconds
# 🍰──────────────────────────────
class CentralLoop(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.loop_task = None

    def cog_unload(self):
        if self.loop_task and not self.loop_task.done():
            self.loop_task.cancel()
            pretty_log(
                "warn",
                "Loop task cancelled on cog unload.",
                label="CENTRAL LOOP",
                bot=self.bot,
            )

    async def central_loop(self):
        """Background loop that ticks every 60 seconds"""
        await self.bot.wait_until_ready()
        from utils.cache.monthly_goal_tracker_cache import flush_monthly_goal_cache
        from utils.cache.weekly_goal_tracker_cache import flush_weekly_goal_cache

        pretty_log(
            "",
            "✅ Central loop started!",
            label="🧭 CENTRAL LOOP",
            bot=self.bot,
        )
        while not self.bot.is_closed():
            try:
                """pretty_log(
                    "",
                    "🔂 Running background checks...",
                    label="🧭 CENTRAL LOOP",
                    bot=self.bot,
                )"""

                # ⏰ Check if any special battle timers are due
                await special_battle_timer_checker(bot=self.bot)

                # 🎅 Check if any Secret Santa reminders are due
                await secret_santa_timer_checker(bot=self.bot)

                # 💎 Check if shiny bonus has expired
                await check_and_handle_expired_shiny_bonus(bot=self.bot)

                # 🧼 Flush weekly goal cache
                await flush_weekly_goal_cache(bot=self.bot)

                # 🧼 Flush monthly goal cache
                await flush_monthly_goal_cache(bot=self.bot)

                # ⏰ Check and trigger due reminders
                await check_and_trigger_reminders(bot=self.bot)

            except Exception as e:
                pretty_log(
                    "error",
                    f"{e}",
                    label="CENTRAL LOOP ERROR",
                    bot=self.bot,
                )
            await asyncio.sleep(60)  # ⏱ tick interval

    @commands.Cog.listener()
    async def on_ready(self):
        """Start the loop automatically once the bot is ready"""
        if not self.loop_task:
            self.loop_task = asyncio.create_task(self.central_loop())


# ====================
# 🔹 Setup
# ====================
async def setup(bot: commands.Bot):
    cog = CentralLoop(bot)
    await bot.add_cog(cog)

    print("\n[📋 CENTRAL LOOP CHECKLIST] Scheduled tasks loaded:")
    print("  ─────────────────────────────────────────────")
    print("  ✅ ⏰  special_battle_timer_checker")
    print("  ✅ 🎅  secret_santa_timer_checker")
    print("  ✅ 💎  shiny_bonus_checker")
    print("  ✅ 🧼  weekly_goal_tracker_cache_flush")
    print("  ✅ 🧼  monthly_goal_tracker_cache_flush")
    print("  ✅ ⏰  reminders_checker")
    print("  🧭 CentralLoop ticking every 60 seconds!")
    print("  ─────────────────────────────────────────────\n")

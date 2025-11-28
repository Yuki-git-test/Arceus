import discord
from discord.ext import commands

from Constants.variables import (
    CC_BUMP_CHANNEL_ID,
    CC_GUILD_ID,
    POKEMEOW_APPLICATION_ID,
    PublicChannels,
    Server,
)
from utils.listener_func.ee_spawn_listener import (
    check_cc_bump_reminder,
    check_ee_near_spawn_alert,
    extract_boss_from_wb_command_embed,
    extract_boss_from_wb_spawn_command,
)
from utils.listener_func.market_feed_listener import market_feeds_listener
from utils.listener_func.pokespawn_listener import as_spawn_ping
from utils.logs.pretty_log import pretty_log
from vn_allstars_constants import VN_ALLSTARS_TEXT_CHANNELS

MARKET_FEED_CHANNEL_IDS = {
    VN_ALLSTARS_TEXT_CHANNELS.c_u_r_s_feed,
    VN_ALLSTARS_TEXT_CHANNELS.golden_feed,
    VN_ALLSTARS_TEXT_CHANNELS.shiny_feed,
    VN_ALLSTARS_TEXT_CHANNELS.l_m_gmax_feed,
}
triggers = {
    "wb_spawn": "spawned a world boss using 1x <:boss_coin:1249165805095092356>",
    "wb_command": "a world boss has spawned! register now!",
    "ee_vote_checker": "there is no active world boss",
}


# 🐾────────────────────────────────────────────
#        🌸 Message Create Listener Cog
# 🐾────────────────────────────────────────────
class MessageCreateListener(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # 🦋────────────────────────────────────────────
    #           👂 Message Listener Event
    # 🦋────────────────────────────────────────────
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        try:
            # 🚫 Ignore all bots except PokéMeow to prevent loops
            if (
                message.author.bot
                and message.author.id != POKEMEOW_APPLICATION_ID
                and not message.webhook_id
            ):
                return

            # ————————————————————————————————
            # 🏰 Guild Check — Route by server
            # ————————————————————————————————
            guild = message.guild
            if not guild:
                return  # Skip DMs

            # ————————————————————————————————
            # 🩵 CC Bump Reminder Listener
            # ————————————————————————————————
            if guild.id == CC_GUILD_ID:
                if message.channel.id == CC_BUMP_CHANNEL_ID:
                    await check_cc_bump_reminder(self.bot, message)
                    
            # ————————————————————————————————
            # 🩵 VNA message logic
            # ————————————————————————————————
            if guild.id == Server.VNA_ID:
                # ————————————————————————————————
                # 🩵 VNA Autospawn
                # ————————————————————————————————
                if message.channel.id == PublicChannels.Poke_Spawn:
                    await as_spawn_ping(self.bot, message)

                # ————————————————————————————————
                # 🩵 VNA Market Snipe
                # ————————————————————————————————
                if message.channel.id in MARKET_FEED_CHANNEL_IDS:
                    await market_feeds_listener(message)

                # 🔧───────────────────────────────────────────────🔧
                # 🔧    🩵 World Boss Spawn Listener
                # 🔧───────────────────────────────────────────────🔧
                if message.content:
                    if triggers["wb_spawn"] in message.content.lower():
                        pretty_log(
                            "info",
                            f"Detected world boss spawn message from PokéMeow bot: Message ID {message.id}",
                            label="World Boss Spawn Listener",
                        )
                        await extract_boss_from_wb_spawn_command(
                            bot=self.bot, message=message
                        )

                # 🔧───────────────────────────────────────────────🔧
                # 🔧    🩵 World Boss Command Embed Listener
                # 🔧───────────────────────────────────────────────🔧
                if message.embeds:
                    embed_title = (
                        message.embeds[0].title if message.embeds[0].title else ""
                    )
                    if triggers["wb_command"] in embed_title.lower():
                        pretty_log(
                            "info",
                            f"Detected world boss command embed from PokéMeow bot: Message ID {message.id}",
                            label="World Boss Command Embed Listener",
                        )
                        await extract_boss_from_wb_command_embed(
                            bot=self.bot, message=message
                        )

                # 🔧───────────────────────────────────────────────🔧
                # 🔧    🩵 EE Near Spawn Alert Checker
                # 🔧───────────────────────────────────────────────🔧
                if message.embeds:
                    embed_title = (
                        message.embeds[0].title if message.embeds[0].title else ""
                    )
                    if triggers["ee_vote_checker"] in embed_title.lower():
                        pretty_log(
                            "info",
                            f"Detected EE vote checker embed from PokéMeow bot: Message ID {message.id}",
                            label="EE Near Spawn Alert Checker",
                        )
                        await check_ee_near_spawn_alert(bot=self.bot, message=message)

        except Exception as e:
            # 🛑────────────────────────────────────────────
            #        Unhandled on_message Error Handler
            # 🛑────────────────────────────────────────────
            pretty_log(
                "critical",
                f"Unhandled exception in on_message: {e}",
                label="MESSAGE",
                bot=self.bot,
                include_trace=True,
            )


# 🌈────────────────────────────────────────────
#        🛠️ Setup function to add cog to bot
# 🌈────────────────────────────────────────────
async def setup(bot: commands.Bot):
    await bot.add_cog(MessageCreateListener(bot))

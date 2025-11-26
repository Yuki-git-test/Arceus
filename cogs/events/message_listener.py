import discord
from discord.ext import commands

from Constants.variables import POKEMEOW_APPLICATION_ID, PublicChannels, Server
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

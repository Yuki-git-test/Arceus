import re

import discord
from discord.ext import commands

from Constants.variables import (
    CC_BUMP_CHANNEL_ID,
    CC_GUILD_ID,
    POKEMEOW_APPLICATION_ID,
    VNA_SERVER_ID,
    PublicChannels,
    Server,
)
from utils.listener_func.explore_caught_listener import explore_caught_listener
from utils.listener_func.fish_spawn_listener import fish_spawn_listener
from utils.listener_func.monthly_stats_listener import monthly_stats_listener
from utils.listener_func.pokemon_caught_listener import pokemon_caught_listener
from utils.listener_func.weekly_stats_listener import weekly_stats_listener
from utils.logs.pretty_log import pretty_log

# ️────────────────────────────────────────────
#        ⚔️ Message Triggers
# ️────────────────────────────────────────────
triggers = {
    "weekly_stats_command": "**Clan Weekly Stats — VN Allstar**",
    "monthly_stats_command": "**Clan Monthly Stats — VN Allstar**",
    "explore_listener": ":stopwatch: Your explore session has ended!",
    "caught_listener": "You caught a",
}


# 🍭──────────────────────────────
#   🎀 Event: On Message Edit
# 🍭──────────────────────────────
class OnMessageEditCog(commands.Cog):
    """Cog to handle message edit events."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):

        # Ignore edits made by bots except PokéMeow
        if after.author.bot and after.author.id != POKEMEOW_APPLICATION_ID:
            return

        content = after.content if after.content else ""
        first_embed = after.embeds[0] if after.embeds else None
        first_embed_author_text = (
            first_embed.author.name if first_embed and first_embed.author else ""
        )
        first_embed_description = first_embed.description if first_embed else ""
        first_embed_footer_text = (
            first_embed.footer.text if first_embed and first_embed.footer else ""
        )
        first_embed_title = first_embed.title if first_embed else ""

        # ————————————————————————————————
        # 🩵 VNA Edit Listener
        # ————————————————————————————————
        # Only log edits in VNA server
        if not after.guild or after.guild.id != VNA_SERVER_ID:
            return

        # ————————————————————————————————
        # 🩵 VNA Fish Spawn Listener
        # ————————————————————————————————
        if (
            first_embed_description
            and "fished a wild" in first_embed_description.lower()
        ):
            await fish_spawn_listener(self.bot, before, after)
        # ————————————————————————————————
        # 🩵 VNA Pokemon Caught Listener
        # ————————————————————————————————
        if first_embed:
            if triggers["caught_listener"] in first_embed_description:
                pretty_log(
                    "info",
                    f"Detected edit triggering VNA Pokemon Caught Listener in {after.channel.name}",
                )
                await pokemon_caught_listener(self.bot, before, after)

        # ————————————————————————————————
        # 🩵 VNA Weekly Stats Listener
        # ————————————————————————————————
        if first_embed:
            if triggers["weekly_stats_command"] in first_embed_title:
                pretty_log(
                    "info",
                    f"Detected edit triggering VNA Weekly Stats Listener in {after.channel.name}",
                )
                await weekly_stats_listener(self.bot, before, after)
        # ————————————————————————————————
        # 🩵 VNA Monthly Stats Listener
        # ————————————————————————————————
        if first_embed:
            if triggers["monthly_stats_command"] in first_embed_title:

                pretty_log(
                    "info",
                    f"Detected edit triggering VNA Monthly Stats Listener in {after.channel.name}",
                )
                await monthly_stats_listener(self.bot, before, after)

        # ————————————————————————————————
        # 🩵 VNA Explore Caught Listener
        # ————————————————————————————————
        if content:
            if triggers["explore_listener"] in content:
                pretty_log(
                    "info",
                    f"Detected edit triggering VNA Explore Caught Listener in {after.channel.name}",
                )
                await explore_caught_listener(self.bot, before, after)


async def setup(bot: commands.Bot):
    await bot.add_cog(OnMessageEditCog(bot))

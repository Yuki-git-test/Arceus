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
from utils.listener_func.fish_spawn_listener import fish_spawn_listener
from utils.logs.pretty_log import pretty_log


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
        # 🩵 CC Edit Listener
        # ————————————————————————————————
        """if after.guild and after.guild.id == CC_GUILD_ID:
            # Check for fish spawn edits
            pass"""
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
            pretty_log(
                "info",
                f"Detected fish spawn edit in CC guild for message ID: {after.id}",
            )
            await fish_spawn_listener(self.bot, before, after)


async def setup(bot: commands.Bot):
    await bot.add_cog(OnMessageEditCog(bot))

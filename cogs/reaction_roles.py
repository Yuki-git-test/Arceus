import discord
from discord.ext import commands
from discord import app_commands
from Constants.variables import PublicChannels, Roles, Emojis  # match your filename/folder

class ReactionRoles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.message_id = None  # Stores the reaction role message ID

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        if payload.message_id != self.message_id:
            return

        guild = self.bot.get_guild(payload.guild_id)
        if not guild:
            return

        member = guild.get_member(payload.user_id)
        if not member or member.bot:
            return

        emoji = str(payload.emoji)

        # Rare Hunter reaction
        if emoji == Emojis.Rare_hunter:
            booster_role = guild.get_role(Roles.Server_Booster)
            if booster_role not in member.roles:
                try:
                    await member.send("❌ You must be a **Server Booster** to get the Rare Hunter role!")
                except discord.Forbidden:
                    pass
                return

            role = guild.get_role(Roles.Rare_Hunter)
            await member.add_roles(role)
            try:
                await member.send("✅ You have been given the **Rare Hunter** role!")
            except discord.Forbidden:
                pass

        # Spawn Hunter reaction
        elif emoji == Emojis.Spawn_hunter:
            role = guild.get_role(Roles.Spawn_Hunter)
            await member.add_roles(role)
            try:
                await member.send("✅ You have been given the **Spawn Hunter** role!")
            except discord.Forbidden:
                pass

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        if payload.message_id != self.message_id:
            return

        guild = self.bot.get_guild(payload.guild_id)
        if not guild:
            return

        member = guild.get_member(payload.user_id)
        if not member or member.bot:
            return

        emoji = str(payload.emoji)

        if emoji == Emojis.Rare_hunter:
            role = guild.get_role(Roles.Rare_Hunter)
            await member.remove_roles(role)
        elif emoji == Emojis.Spawn_hunter:
            role = guild.get_role(Roles.Spawn_Hunter)
            await member.remove_roles(role)

    @app_commands.command(name="setup_reactionroles", description="Setup the reaction roles message.")
    @app_commands.checks.has_permissions(administrator=True)
    async def setup_reactionroles(self, interaction: discord.Interaction):
        """Creates and sends the reaction role message."""
        embed = discord.Embed(
            title="<a:bl_crown:1396426278818549780> Reaction Roles",
            description=(
                f"{Emojis.Rare_hunter} — <@&{Roles.Rare_Hunter}> *(Server Boosters only)*\n"
                f"{Emojis.Spawn_hunter} — <@&{Roles.Spawn_Hunter}> *(Everyone can claim)*"
            ),
            color=discord.Color.gold()
        )

        channel = interaction.guild.get_channel(PublicChannels.Roles)
        message = await channel.send(embed=embed)

        # Extract emoji objects so bot can react properly
        rare_emoji = await self._extract_emoji(interaction, Emojis.Rare_hunter)
        spawn_emoji = await self._extract_emoji(interaction, Emojis.Spawn_hunter)

        await message.add_reaction(rare_emoji)
        await message.add_reaction(spawn_emoji)

        self.message_id = message.id
        await interaction.response.send_message("✅ Reaction role message created!", ephemeral=True)

    async def _extract_emoji(self, interaction, emoji_string):
        """Extracts a proper Emoji object or Unicode string from '<:name:id>' format."""
        if emoji_string.startswith("<:") or emoji_string.startswith("<a:"):
            parts = emoji_string.strip("<>").split(":")
            emoji_id = int(parts[-1])
            emoji = interaction.client.get_emoji(emoji_id)
            return emoji
        return emoji_string


async def setup(bot):
    await bot.add_cog(ReactionRoles(bot))

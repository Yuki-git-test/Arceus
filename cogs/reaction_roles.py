import json
import os

import discord
from discord import app_commands
from discord.ext import commands

from Constants.variables import Emojis  # match your filename/folder
from Constants.variables import PublicChannels, Roles
from utils.logs.pretty_log import pretty_log


class ReactionRoles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.message_id = self._load_message_id()

    def _load_message_id(self):
        config_path = "Data/reaction_roles_config.json"
        if os.path.exists(config_path):
            try:
                with open(config_path, "r") as f:
                    data = json.load(f)
                    return data.get("message_id")
            except Exception:
                pass
        return None

    def _save_message_id(self, message_id):
        config_path = "Data/reaction_roles_config.json"
        data = {"message_id": message_id}
        try:
            with open(config_path, "w") as f:
                json.dump(data, f)
        except Exception:
            pass

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
                    await member.send(
                        "❌ You must be a **Server Booster** to get the Rare Hunter role!"
                    )
                    pretty_log(
                        message=f"❌ Could not assign Rare Hunter role to {member} due to lack of booster status.",
                        tag="error",
                    )
                except discord.Forbidden:
                    pretty_log(
                        message=f"❌ Could not send DM to {member} about Rare Hunter role requirement.",
                        tag="info",
                    )
                return

            role = guild.get_role(Roles.Rare_Hunter)
            try:
                await member.add_roles(role)
                pretty_log(
                    message=f"✅ Assigned Rare Hunter role to {member}.", tag="success"
                )
            except discord.Forbidden:
                pretty_log(
                    message=f"❌ Could not assign Rare Hunter role to {member}.",
                    tag="error",
                )
            try:
                await member.send("✅ You have been given the **Rare Hunter** role!")
                pretty_log(
                    message=f"✅ Assigned Rare Hunter role to {member}.", tag="success"
                )
            except discord.Forbidden:
                pretty_log(
                    message=f"❌ Could not send DM to {member} about Rare Hunter role.",
                    tag="info",
                )

        # Spawn Hunter reaction
        elif emoji == Emojis.Spawn_hunter:
            role = guild.get_role(Roles.Spawn_Hunter)
            try:
                await member.add_roles(role)
                pretty_log(
                    message=f"✅ Assigned Spawn Hunter role to {member}.", tag="success"
                )
            except discord.Forbidden:
                pretty_log(
                    message=f"❌ Could not assign Spawn Hunter role to {member}.",
                    tag="error",
                )
            try:
                await member.send("✅ You have been given the **Spawn Hunter** role!")
            except discord.Forbidden:
                pretty_log(
                    message=f"❌ Could not send DM to {member} about Spawn Hunter role.",
                    tag="info",
                )

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
            try:
                await member.remove_roles(role)
                pretty_log(
                    message=f"✅ Removed Rare Hunter role from {member}.", tag="success"
                )
                # Notify user via DM
                try:
                    await member.send("✅ Your **Rare Hunter** role has been removed.")
                    pretty_log(
                        message=f"✅ Sent DM to {member} about Rare Hunter role removal.",
                        tag="success",
                    )
                except discord.Forbidden:
                    pretty_log(
                        message=f"❌ Could not send DM to {member} about Rare Hunter role removal.",
                        tag="info",
                    )
            except discord.Forbidden:
                pretty_log(
                    message=f"❌ Could not remove Rare Hunter role from {member}.",
                    tag="error",
                )
        elif emoji == Emojis.Spawn_hunter:
            role = guild.get_role(Roles.Spawn_Hunter)
            try:
                await member.remove_roles(role)
                pretty_log(
                    message=f"✅ Removed Spawn Hunter role from {member}.",
                    tag="success",
                )
                # Notify user via DM
                try:
                    await member.send("✅ Your **Spawn Hunter** role has been removed.")
                    pretty_log(
                        message=f"✅ Sent DM to {member} about Spawn Hunter role removal.",
                        tag="success",
                    )
                except discord.Forbidden:
                    pretty_log(
                        message=f"❌ Could not send DM to {member} about Spawn Hunter role removal.",
                        tag="info",
                    )
            except discord.Forbidden:
                pretty_log(
                    message=f"❌ Could not remove Spawn Hunter role from {member}.",
                    tag="error",
                )

    @app_commands.command(
        name="setup_reactionroles", description="Setup the reaction roles message."
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def setup_reactionroles(self, interaction: discord.Interaction):
        """Creates and sends the reaction role message."""
        embed = discord.Embed(
            title="<a:bl_crown:1396426278818549780> Reaction Roles",
            description=(
                f"{Emojis.Rare_hunter} — <@&{Roles.Rare_Hunter}> *(Server Boosters only)*\n"
                f"{Emojis.Spawn_hunter} — <@&{Roles.Spawn_Hunter}> *(Everyone can claim)*"
            ),
            color=discord.Color.gold(),
        )

        channel = interaction.guild.get_channel(PublicChannels.Roles)
        message = await channel.send(embed=embed)

        # Extract emoji objects so bot can react properly
        rare_emoji = await self._extract_emoji(interaction, Emojis.Rare_hunter)
        spawn_emoji = await self._extract_emoji(interaction, Emojis.Spawn_hunter)

        await message.add_reaction(rare_emoji)
        await message.add_reaction(spawn_emoji)

        self.message_id = message.id
        self._save_message_id(message.id)
        await interaction.response.send_message(
            "✅ Reaction role message created!", ephemeral=True
        )

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

import discord
from discord.ui import Button, View

from Constants.clan_wars_constants import CLAN_WARS_ROLES
from Constants.vn_allstars_constants import ARCEUS_EMBED_COLOR
from utils.logs.pretty_log import pretty_log

ROLES_EMOJI = "⚜️"


# 🍬 Helper: Format the role list into an embed-friendly description
def format_role_description(line: list[tuple[str, discord.Role]]) -> str:
    parts = []
    for emoji, role in line:
        parts.append(f"{emoji} {role.mention}")
    return "\n".join(parts)


class ToggleRoleButton(Button):
    def __init__(self, role: discord.Role, label: str, emoji: str):
        super().__init__(
            style=discord.ButtonStyle.secondary,
            emoji=emoji,
            custom_id=f"toggle_role_{role.id}",
        )
        self.role = role

    async def callback(self, interaction: discord.Interaction):
        member = interaction.user
        role = self.role
        try:
            if role in member.roles:
                await member.remove_roles(role)
                pretty_log(f"Removed role {role.name} from {member.display_name}")
                await interaction.response.send_message(
                    f"Removed role **{role.mention}** from you", ephemeral=True
                )
            else:
                await member.add_roles(role)
                pretty_log(f"Added role {role.name} to {member.display_name}")
                await interaction.response.send_message(
                    f"Added role **{role.mention}** to you", ephemeral=True
                )
        except Exception as e:
            pretty_log(
                f"Error toggling role {role.name} for {member.display_name}: {e}"
            )
            await interaction.response.send_message(
                "An error occurred while trying to update your roles.", ephemeral=True
            )


class General_Roles_Button(Button):
    def __init__(self):
        super().__init__(
            style=discord.ButtonStyle.secondary,
            emoji=ROLES_EMOJI,
            custom_id="general_roles_button",
        )

    async def callback(self, interaction: discord.Interaction):
        try:
            guild = interaction.guild
            user = interaction.user
            view, embed = build_general_roles_embed(guild, user)
            if view and embed:
                await interaction.response.send_message(
                    embed=embed,
                    view=view,
                    ephemeral=True,
                )
            else:
                await interaction.response.send_message(
                    "An error occurred while building the roles embed.",
                    ephemeral=True,
                )
                pretty_log(
                    "error",
                    f"Failed to build General Roles Embed for {interaction.user.display_name}",
                )
        except Exception as e:
            pretty_log(
                f"Error in General Roles Button callback for {interaction.user.display_name}: {e}"
            )
            await interaction.response.send_message(
                "An error occurred while processing your request.", ephemeral=True
            )


def build_general_roles_embed(guild: discord.Guild, user: discord.Member):
    try:
        view = discord.ui.View(timeout=None)

        # General Roles
        giveaway_role = guild.get_role(CLAN_WARS_ROLES.giveaway)
        autospawn_ping_role = guild.get_role(CLAN_WARS_ROLES.autospawn_ping)
        rare_autospawn_ping_role = guild.get_role(CLAN_WARS_ROLES.rare_autospawn_ping)

        roles = []
        if giveaway_role:
            emoji = "🎁"
            view.add_item(ToggleRoleButton(giveaway_role, "Giveaway", emoji))
            roles.append((emoji, giveaway_role))

        if autospawn_ping_role:
            emoji = "⚡"
            view.add_item(
                ToggleRoleButton(autospawn_ping_role, "Autospawn Ping", emoji)
            )
            roles.append((emoji, autospawn_ping_role))

        if rare_autospawn_ping_role:
            emoji = "✨"
            view.add_item(
                ToggleRoleButton(rare_autospawn_ping_role, "Rare Autospawn Ping", emoji)
            )
            roles.append((emoji, rare_autospawn_ping_role))

        if roles:
            description = format_role_description(roles)
        else:
            description = "No general roles available at the moment."

        title = f"{ROLES_EMOJI} General Roles"
        embed = discord.Embed(
            title=title, description=description, color=ARCEUS_EMBED_COLOR
        )
        return view, embed

    except Exception as e:
        pretty_log("error", f"Error building General Roles Embed: {e}")
        return None, None

import discord
from discord.ui import Button, View

from Constants.clan_wars import PARTICIPATING_CLANS
from Constants.clan_wars_constants import CLAN_WARS_ROLES
from Constants.vn_allstars_constants import ARCEUS_EMBED_COLOR
from utils.db.clan_wars_server_members import get_member_clan_name
from utils.logs.pretty_log import pretty_log

from .general_roles_embed import ToggleRoleButton, format_role_description

ROLES_EMOJI = "🏰"


class Clan_Wars_Roles_Button(Button):
    def __init__(self):
        super().__init__(
            style=discord.ButtonStyle.secondary,
            emoji=ROLES_EMOJI,
            custom_id="clan_wars_roles_button",
        )

    async def callback(self, interaction: discord.Interaction):
        from utils.cache.clan_wars_cache import get_member_clan_name_cache

        member = interaction.user
        guild = interaction.guild
        clan_name = get_member_clan_name_cache(member.id)
        try:
            if clan_name:
                # Check if clan is participating
                if clan_name in PARTICIPATING_CLANS:
                    embed, view = build_clan_wars_roles_embed(clan_name, guild)
                    if embed and view:
                        await interaction.response.send_message(
                            embed=embed, view=view, ephemeral=True
                        )
                    else:
                        await interaction.response.send_message(
                            "Error building roles embed. Please try again later.",
                            ephemeral=True,
                        )
                else:
                    await interaction.response.send_message(
                        f"Your clan ({clan_name}) is not currently participating in Clan Wars.",
                        ephemeral=True,
                    )
            else:
                await interaction.response.send_message(
                    "You don't have a clan associated with your account. Please use the ;stats command to set your clan.",
                    ephemeral=True,
                )
        except Exception as e:
            pretty_log(
                f"Error handling Clan Wars Roles Button interaction for {member.display_name}: {e}"
            )
            await interaction.response.send_message(
                "An error occurred while trying to fetch clan wars roles.",
                ephemeral=True,
            )


def build_clan_wars_roles_embed(clan_name: str, guild: discord.Guild) -> discord.Embed:
    # Fetch clan roles
    clan_info = PARTICIPATING_CLANS.get(clan_name)
    clan_role_id = clan_info["clan_role"] if clan_info else None
    supporter_role_id = clan_info["supporter_role"] if clan_info else None
    clan_role = guild.get_role(clan_role_id) if clan_role_id else None
    supporter_role = guild.get_role(supporter_role_id) if supporter_role_id else None
    roles = []
    try:
        view = discord.ui.View(timeout=None)
        if clan_role:
            emoji = "⚔️"
            role_name = clan_role.name
            view.add_item(ToggleRoleButton(clan_role, role_name, emoji))
            roles.append((emoji, clan_role))
        if supporter_role:
            emoji = "🛡️"
            role_name = supporter_role.name
            view.add_item(ToggleRoleButton(supporter_role, role_name, emoji))
            roles.append((emoji, supporter_role))
        if roles:
            description = format_role_description(roles)
        else:
            description = "No roles available for this clan at the moment."
        title = f"{ROLES_EMOJI} {clan_name} Roles"
        embed = discord.Embed(
            title=title, description=description, color=ARCEUS_EMBED_COLOR
        )
        return embed, view

    except Exception as e:
        pretty_log(
            "error",
            f"Error building Clan Wars Roles Embed for guild '{guild.name}': {e}",
        )
        return None

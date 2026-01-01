import re
from datetime import datetime

import discord

from Constants.aesthetic import Emojis, Thumbnails
from Constants.vn_allstars_constants import (
    VN_ALLSTARS_EMOJIS,
    VN_ALLSTARS_ROLES,
    VN_ALLSTARS_TEXT_CHANNELS,
)
from utils.cache.cache_list import ping_message_id_cache
from utils.db.ping_message_ids_db import (
    delete_ping_message_id,
    get_ping_message_id,
    upsert_ping_message_id,
)
from utils.logs.debug_log import debug_log, enable_debug
from utils.logs.pretty_log import pretty_log
from utils.pokemeow.get_pokemeow_reply import get_pokemeow_reply_member

# enable_debug(f"{__name__}.incense_command_handler")
TEAL_COLOR = 0x7FDBDA
INCENSE = Emojis.incense


class ToggleIncensePingButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Toggle Incense Ping",
        emoji=INCENSE,
        style=discord.ButtonStyle.secondary,
        custom_id="toggle_incense_ping_button",
    )
    async def toggle_incense_ping(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        incense_ping_role = interaction.guild.get_role(VN_ALLSTARS_ROLES.incense_ping)
        if not incense_ping_role:
            await interaction.response.send_message(
                "Incense Ping role not found in this server.", ephemeral=True
            )
            return
        member = interaction.user
        if incense_ping_role in member.roles:
            await member.remove_roles(incense_ping_role)
            await interaction.response.send_message(
                f"Removed {incense_ping_role.mention} from you.", ephemeral=True
            )
        else:
            await member.add_roles(incense_ping_role)
            await interaction.response.send_message(
                f"Added {incense_ping_role.mention} to you.", ephemeral=True
            )


def extract_incense_charge_and_amount(message_content: str):
    charges_match = re.search(
        r"This boost has \*\*([\d,]+)\*\* charges", message_content or ""
    )
    total_charges = (
        int(charges_match.group(1).replace(",", "")) if charges_match else None
    )
    amount_match = re.search(r"\*\*(\d+)x\*\*", message_content or "")
    amount = int(amount_match.group(1)) if amount_match else None
    return total_charges, amount


def build_incense_embed(
    guild: discord.Guild,
    total_charges: int,
    amount: int,
    member_name: str,
):
    desc = f"""### {guild.name} has {INCENSE} {total_charges} incense charges remaining.
> - 1 charge is consumed per `;pokemon` or `;fish` encounter,
> - Use an incense with `;incense use <amount>`
> - Incense charges are shared & used by every player in this server

**{INCENSE} Incense benefits**:
> - +10% increased {VN_ALLSTARS_EMOJIS.vna_shiny} shiny rate (for `;pokemon` & `;fish`)
> - +10% increased `;promo` rates
> - 1 charge used on encounters, battles, and egg hatches during promo"""
    embed = discord.Embed(
        description=desc,
        timestamp=datetime.now(),
        color=TEAL_COLOR,
    )
    footer_text = (
        f"{amount} incense used by {member_name}."
        if member_name
        else f"{guild.name} has incense charges."
    )
    embed.set_footer(
        text=f"{footer_text} | Updated ",
        icon_url=guild.icon.url if guild.icon else None,
    )
    embed.set_thumbnail(url=Thumbnails.incense)
    return embed


async def incense_use_handler(
    bot: discord.Client,
    message: discord.Message,
):

    # Check if there is already a message id stored
    from utils.cache.ping_message_id_cache import get_ping_message_id_incense

    existing_message_id = get_ping_message_id_incense()
    if existing_message_id:
        return
    else:
        # Check db
        db_message_id = await get_ping_message_id(bot, type="incense")
        if db_message_id:
            return

    member = await get_pokemeow_reply_member(message)
    if not member:
        return
    total_charges, amount = extract_incense_charge_and_amount(message.content)
    if total_charges is None or amount is None:
        return

    guild = message.guild
    bump_channel = guild.get_channel(VN_ALLSTARS_TEXT_CHANNELS.bumps)
    incense_ping_role = guild.get_role(VN_ALLSTARS_ROLES.incense_ping)
    content = (
        f"{incense_ping_role.mention} The server has {total_charges} incense charges!"
    )
    embed = build_incense_embed(
        guild,
        total_charges,
        amount,
        member.name,
    )
    sent_msg = await bump_channel.send(content=content, embed=embed, view=ToggleIncensePingButton())

    # Upsert in db
    await upsert_ping_message_id(
        bot,
        type="incense",
        message_id=sent_msg.id,
    )


async def server_has_incense_handler(
    bot: discord.Client,
    message: discord.Message,
):

    # Check if there is already a message id stored
    from utils.cache.ping_message_id_cache import get_ping_message_id_incense

    existing_message_id = get_ping_message_id_incense()
    if existing_message_id:
        return
    else:
        # Check db
        db_message_id = await get_ping_message_id(bot, type="incense")
        if db_message_id:
            return

    guild = message.guild
    bump_channel = guild.get_channel(VN_ALLSTARS_TEXT_CHANNELS.bumps)
    incense_ping_role = guild.get_role(VN_ALLSTARS_ROLES.incense_ping)
    content = f"{incense_ping_role.mention} The server has incense charges!"
    desc = f"""### {guild.name} has {INCENSE} incense charges.
> - 1 charge is consumed per `;pokemon` or `;fish` encounter,
> - Use an incense with `;incense use <amount>`
> - Incense charges are shared & used by every player in this server

**{INCENSE} Incense benefits**:
> - +10% increased {VN_ALLSTARS_EMOJIS.vna_shiny} shiny rate (for `;pokemon` & `;fish`)
> - +10% increased `;promo` rates
> - 1 charge used on encounters, battles, and egg hatches during promo"""
    embed = discord.Embed(
        description=desc,
        color=TEAL_COLOR,
    )
    embed.set_footer(
        text=f"{guild.name} has incense charges. | Updated ",
        icon_url=guild.icon.url if guild.icon else None,
    )
    embed.set_thumbnail(url=Thumbnails.incense)
    sent_msg = await bump_channel.send(content=content, embed=embed, view=ToggleIncensePingButton())

    # Upsert in db
    await upsert_ping_message_id(
        bot,
        type="incense",
        message_id=sent_msg.id,
    )


async def incense_command_handler(
    bot: discord.Client,
    message: discord.Message,
):
    new_incense_msg = False
    # Check if there is already a message id stored
    from utils.cache.ping_message_id_cache import get_ping_message_id_incense

    existing_message_id = get_ping_message_id_incense()
    debug_log(
        f"incense_command_handler: cache incense message ID: {existing_message_id}"
    )
    if not existing_message_id:
        debug_log(f"No existing incense message ID in cache.")
        # Double check db
        db_message_id = await get_ping_message_id(bot, type="incense")
        debug_log(f"incense_command_handler: db incense message ID: {db_message_id}")
        if db_message_id:
            existing_message_id = db_message_id
        else:
            new_incense_msg = True

    embed = message.embeds[0]
    if not embed:
        debug_log("incense_command_handler: No embed found in message.")
        return

    embed_desc = embed.description
    if not embed_desc:
        debug_log("incense_command_handler: No embed description found.")
        return

    username = None
    # Extract charges remaining
    charges_match = re.search(
        r"has\s+(?:<:[\w\d_]+:\d+>\s+)?<:incense:\d+>\s+\*\*([\d,]+)\*\*\s+incense charges remaining",
        embed_desc,
    )
    remaining_charges = (
        int(charges_match.group(1).replace(",", "")) if charges_match else 0
    )
    if not charges_match:
        pretty_log(
            "info",
            "Failed to extract remaining incense charges from embed description.",
        )

    amount = 0
    # Extract the most recent contributor
    contributor_matches = re.findall(
        r"\*\*(.+?)\*\* activated .*? (\d+)x Incense(?:s)?(?: for [\d,]+ charges)?",
        embed_desc,
    )

    debug_log(f"incense_command_handler: Remaining charges: {remaining_charges}")
    if remaining_charges == 0:
        debug_log(
            "incense_command_handler: Remaining charges is 0, calling incense_depleted_handler."
        )
        await incense_depleted_handler(bot, message)
        return

    if contributor_matches:
        username, amount = contributor_matches[-1]
        debug_log(f"incense_command_handler: Contributor: {username}, Amount: {amount}")
        pretty_log(
            "info",
            f"Incense used by {username}, amount: {amount}, remaining charges: {remaining_charges}",
        )
    if not contributor_matches:
        debug_log(
            "incense_command_handler: Failed to extract contributor and amount from embed description."
        )
        pretty_log(
            "info",
            "Failed to extract contributor and amount from embed description.",
        )
    embed = build_incense_embed(
        guild=message.guild,
        total_charges=remaining_charges,
        amount=amount,
        member_name=username,
    )
    bump_channel = message.guild.get_channel(VN_ALLSTARS_TEXT_CHANNELS.bumps)
    incense_ping_role = message.guild.get_role(VN_ALLSTARS_ROLES.incense_ping)
    if new_incense_msg:
        debug_log("incense_command_handler: Creating new incense message.")
        content = f"{incense_ping_role.mention} The server has {remaining_charges} incense charges!"
        sent_msg = await bump_channel.send(content=content, embed=embed, view=ToggleIncensePingButton())
        # Upsert in db
        await upsert_ping_message_id(
            bot,
            type="incense",
            message_id=sent_msg.id,
        )
        pretty_log(
            "info",
            f"Created new incense message ID {sent_msg.id} in channel {bump_channel.id}",
        )
        debug_log(
            f"incense_command_handler: Created new incense message ID {sent_msg.id} in channel {bump_channel.id}"
        )
    else:
        debug_log(
            f"incense_command_handler: Updating existing message ID {existing_message_id}"
        )
        # Update existing message
        old_msg = await bump_channel.fetch_message(existing_message_id)
        await old_msg.edit(embed=embed)
        pretty_log(
            "info",
            f"Updated incense message ID {existing_message_id} in channel {bump_channel.id}",
        )
        debug_log(
            f"incense_command_handler: Updated incense message ID {existing_message_id} in channel {bump_channel.id}"
        )


async def incense_depleted_handler(
    bot: discord.Client,
    message: discord.Message,
):
    # Check if there is already a message id stored
    from utils.cache.ping_message_id_cache import get_ping_message_id_incense

    existing_message_id = get_ping_message_id_incense()

    if not existing_message_id:
        # Double check db
        db_message_id = await get_ping_message_id(bot, type="incense")
        if db_message_id:
            existing_message_id = db_message_id
        else:
            return

    # Remove from db
    await delete_ping_message_id(
        bot,
        type="incense",
    )

    guild = message.guild
    bump_channel = guild.get_channel(VN_ALLSTARS_TEXT_CHANNELS.bumps)
    incense_ping_role = guild.get_role(VN_ALLSTARS_ROLES.incense_ping)

    content = f"{incense_ping_role.mention} There are no more incense charges."
    await bump_channel.send(content=content)
    # Remove view
    old_msg = await bump_channel.fetch_message(existing_message_id)
    await old_msg.edit(view=None)
    pretty_log(
        "info",
        f"Incense depleted. Removed incense message ID {existing_message_id} view in channel {bump_channel.id}",
    )

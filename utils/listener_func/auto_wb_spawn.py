import asyncio
import json
import os
import random
import re
import time
from tty import CC

import discord
from discord import Object
from discord.ext import commands


from Constants.variables import CC_BUMP_CHANNEL_ID, CC_GUILD_ID
from Constants.vn_allstars_constants import (
    DEFAULT_EMBED_COLOR,
    VN_ALLSTARS_EMOJIS,
    VN_ALLSTARS_ROLES,
    VN_ALLSTARS_TEXT_CHANNELS,
    VNA_SERVER_ID,
    CC_WB_SPAWN_CHANNEL_ID
)
from Constants.world_boss_constants import (
    WB_REGEMOJI,
    WBColors,
    WBEmojis,
    WBGuide,
    WBRegImage,
    WBShinyImage,
    wb_shared_cooldowns,
)
from utils.db.active_wb_db import upsert_active_wb
from utils.essentials.cleanup_first_match import cleanup_first_match
from utils.pokemeow.get_pokemeow_reply import get_pokemeow_reply_or_interaction_member
from utils.logs.debug_log import debug_log, enable_debug
from utils.logs.pretty_log import pretty_log

# ⏳ Keep track of cooldown per guild (shared with slash command ideally)
guild_cooldowns: dict[int, float] = {}  # {guild_id: last_post_time}
cc_shared_cooldowns: dict[int, float] = {}  # {guild_id: last_post_time}

# enable_debug(f"{__name__}.check_cc_bump_reminder")

PLUS_EMOJI = "➕"
CHECK_EMOJI = "✅"


def extract_battle_begins_time_from_wb_command(description: str):
    """
    Extracts the 'Battle begins in' time from the embed description.
    Returns the time string if found, else None.
    """
    match = re.search(r"The battle begins <t:(\d+):R>", description)
    if match:
        return match.group(1).strip()
    return None


async def _cc_wb_reminder_exists(
    channel: discord.TextChannel, title: str, timestamp: str | None
) -> bool:
    timestamp_value = _parse_wb_timestamp(timestamp)
    if timestamp_value is None:
        return False

    member = channel.guild.me
    if member is None or not channel.permissions_for(member).read_message_history:
        message = (
            f"Cannot check CC WB reminder history in {channel.name}: missing access."
        )
        pretty_log("error", message)
        raise PermissionError(message)

    try:
        async for message in channel.history(limit=50):
            if not message.author.bot:
                continue
            for embed in message.embeds:
                if (
                    embed.title or ""
                ).strip().casefold() == title.strip().casefold() and _parse_wb_timestamp(
                    (embed.description or "").strip()
                ) == timestamp_value:
                    return True
    except discord.HTTPException as e:
        pretty_log("error", f"Failed to check CC WB reminder history: {e}")
        raise
    return False


def extract_timestamp_from_wb_spawn_command(description: str):
    match = re.search(r"Challenge starts <t:(\d+):R>", description)
    if match:
        return match.group(1).strip()
    return None


def _parse_wb_timestamp(timestamp: str | None) -> int | None:
    if timestamp and timestamp.isdigit():
        return int(timestamp)
    return None


async def check_cc_bump_reminder(bot: commands.Bot, message: discord.Message):
    embed = message.embeds[0] if message.embeds else None
    if not embed:
        debug_log(
            f"Skipping message {message.id}: no embeds",
        )
        return

    # Return if the bot sent the message
    if message.author.id == bot.user.id:
        debug_log(
            f"Skipping message {message.id}: sent by bot",
        )
        return

    embed_title = embed.title or ""
    embed_description = embed.description or ""

    if embed_title == "Votes left until EE Spawn":
        boss_key = "eternamax-eternatus"
        votes_left = embed_description.strip()
        last_seen_votes[boss_key] = votes_left
        debug_log(
            f"Updated last seen votes for {boss_key}: {votes_left}",
        )
        votes_left_int = int(votes_left.replace(",", ""))  # Handles numbers with commas
        if votes_left_int <= 100 and boss_key not in near_spawn_alert_cache:
            debug_log(
                f"Sending near-spawn alert for {boss_key}: {votes_left} votes left",
            )
            near_spawn_alert_cache.add(boss_key)
            save_vote_cache()  # save after sending alert
            guild = bot.get_guild(VNA_SERVER_ID)
            channel_id = VN_ALLSTARS_TEXT_CHANNELS.world_boss_spawn
            ee_ping_role_id = VN_ALLSTARS_ROLES.ee_spawn_ping

            channel = guild.get_channel(channel_id) or Object(id=channel_id)
            await channel.send(
                f"<@&{ee_ping_role_id}> ⚠️ Only {votes_left} votes left until Eternamax-Eternatus spawns!"
            )

            pretty_log(
                "ready",
                f"Sent near-spawn alert for {boss_key}: {votes_left} votes left from cc  bump reminder",
            )
            await message.add_reaction(PLUS_EMOJI)
    elif "EE Spawned" in embed_title:
        # Check if desc has timestamp for spawned EE
        debug_log(
            f"Checking EE Spawned embed for timestamp: {embed_description}",
        )
        timestamp = embed_description.strip()
        debug_log(f" Sending to auto_wb_ping with timestamp: {timestamp}")
        await auto_wb_ping(
            bot=bot,
            variant="shiny" if "Shiny" in embed_title else "regular",
            boss="eternatus",
            battle_begins_time=timestamp,
            message=message,
        )
    await message.add_reaction(CHECK_EMOJI)


async def check_cc_other_wb_reminder(bot: commands.Bot, message: discord.Message):
    embed = message.embeds[0] if message.embeds else None
    if not embed:
        debug_log(
            f"Skipping message {message.id}: no embeds",
        )
        return

    # Return if the bot sent the message
    if message.author.id == bot.user.id:
        debug_log(
            f"Skipping message {message.id}: sent by bot",
        )
        return

    embed_title = embed.title or ""
    embed_description = embed.description or ""
    timestamp = embed_description.strip()
    boss_name = embed_title.strip().lower() if embed_title else ""
    variant = "shiny" if "shiny" in boss_name else "regular"
    stripped_boss_name = boss_name.replace("shiny ", "")
    debug_log(f" Sending to auto_wb_ping with timestamp: {timestamp}")
    await auto_wb_ping(
        bot=bot,
        variant=variant,
        boss=stripped_boss_name,
        battle_begins_time=timestamp,
        message=message,
    )
    await message.add_reaction(PLUS_EMOJI)
    await message.add_reaction(CHECK_EMOJI)


async def send_cc_bump_reminder(
    bot: commands.Bot,
    context: str,
    votes_left: str = None,
    variant: str = "regular",
    timestamp: str = None,
):

    cc_guild = bot.get_guild(CC_GUILD_ID)
    guild = bot.get_guild(VNA_SERVER_ID)
    cc_bump_channel = cc_guild.get_channel(CC_BUMP_CHANNEL_ID)
    if context == "votes left" and votes_left:
        title = "Votes left until EE Spawn"
        description = votes_left
        color = discord.Color.blue()
        bump_embed = discord.Embed(title=title, description=description, color=color)

        await cc_bump_channel.send(embed=bump_embed)
        pretty_log(
            "success",
            f"Sent CC bump reminder for ee votes left in {cc_bump_channel.name}",
        )
    else:
        description = None
        if timestamp:
            description = timestamp
        else:
            description = "N/A"

        if variant == "shiny":
            title = "Shiny EE Spawned"
            color = WBColors.Shiny
        else:
            title = "EE Spawned"
            color = WBColors.eternatus

        if await _cc_wb_reminder_exists(cc_bump_channel, title, timestamp):
            pretty_log("info", f"CC WB reminder already exists for {title}.")
            return

        # 🕒 Cooldown check
        cooldown_time = 300  # 5 minutes
        now = time.time()
        last_time = cc_shared_cooldowns.get(guild.id, 0)
        elapsed = now - last_time

        if elapsed < cooldown_time:
            pretty_log(
                "info",
                f"Auto WB ping blocked by shared cooldown ({int(cooldown_time - elapsed)}s remaining)",
            )
            return
        # ✅ Update the shared cooldown
        cc_shared_cooldowns[guild.id] = now

        bump_embed = discord.Embed(title=title, description=description, color=color)

        await cc_bump_channel.send(embed=bump_embed)
        pretty_log(
            "success",
            f"Sent CC bump reminder for ee spawn in {cc_bump_channel.name}",
        )


async def send_cc_other_wb_reminder(
    bot: commands.Bot,
    variant: str,
    boss_name: str,
    timestamp: str = None,
):
    formatted_boss_name = boss_name
    if variant == "shiny":
        formatted_boss_name = f"Shiny {boss_name}"
    timestamp_value = _parse_wb_timestamp(timestamp)

    cc_guild = bot.get_guild(CC_GUILD_ID)
    guild = bot.get_guild(VNA_SERVER_ID)
    cc_other_wb_channel = cc_guild.get_channel(CC_WB_SPAWN_CHANNEL_ID)
    is_shiny = False

    if variant == "shiny":
        is_shiny = True

    description = None
    if timestamp:
        description = timestamp
    else:
        description = "N/A"

    if is_shiny:
        color = WBColors.Shiny
    else:
        color = discord.Color.blue()

    title = formatted_boss_name if formatted_boss_name else "Unknown Boss"
    if await _cc_wb_reminder_exists(cc_other_wb_channel, title, timestamp):
        pretty_log("info", f"CC WB reminder already exists for {title}.")
        return

    # 🕒 Cooldown check
    cooldown_time = 300  # 5 minutes
    now = time.time()
    last_time = cc_shared_cooldowns.get(guild.id, 0)
    elapsed = now - last_time

    if elapsed < cooldown_time:
        pretty_log(
            "info",
            f"Auto WB ping blocked by shared cooldown ({int(cooldown_time - elapsed)}s remaining)",
        )
        return
    # ✅ Update the shared cooldown
    cc_shared_cooldowns[guild.id] = now
    bump_embed = discord.Embed(title=title, description=description, color=color)

    await cc_other_wb_channel.send(embed=bump_embed)
    # update active wb
    if timestamp_value is not None:
        await upsert_active_wb(
            bot=bot, boss_name=formatted_boss_name, wb_timestamp=timestamp_value
        )
    pretty_log(
        "success",
        f"Sent CC bump reminder for {formatted_boss_name} spawn in {cc_other_wb_channel.name}",
    )


async def extract_boss_from_wb_spawn_command(
    bot: commands.Bot, message: discord.Message
):
    """
    Extracts boss info & spawned_by user from a WB spawn message and triggers auto ping.
    Works for messages with embeds containing emojis, shiny/regular bosses, and usernames with dots/numbers.
    """
    spawned_by_member = None
    boss_name = None
    variant = "regular"

    try:
        for embed in message.embeds:
            description = embed.description
            if not description:
                continue

            # --- Remove emojis for clean parsing ---
            clean_desc = re.sub(r"<:[\w\d]+:\d+>", "", description)

            # --- Extract boss name & variant ---
            boss_match = re.search(
                r"(Shiny\s+)?(?:Gigantamax|Eternamax)-([\w-]+)",
                clean_desc,
                re.IGNORECASE,
            )
            if boss_match:
                shiny_prefix, boss_name = boss_match.groups()
                variant = "shiny" if shiny_prefix else "regular"

            # Extract battle begins time
            battle_begins_time = extract_timestamp_from_wb_spawn_command(description)

            # --- Extract spawned by user ---
            spawn_match = re.search(r"Spawned by:\s*(.+)", description)
            if spawn_match:
                spawned_by_raw = spawn_match.group(1).strip()
                # Remove any emojis if included
                spawned_by_raw = re.sub(r"<:[\w\d]+:\d+>", "", spawned_by_raw).strip()
                # Take only the username part before the # if present
                spawned_by_name = spawned_by_raw.split("#")[0].strip()
                spawned_by_member = message.guild.get_member_named(spawned_by_name)

    except Exception as e:
        pretty_log(
            "error",
            f"Failed to extract boss/spawn info: {e}",
        )
        return

    # Trigger auto ping with extracted info
    await auto_wb_ping(
        bot=bot,
        message=message,
        variant=variant,
        boss=boss_name,
        spawned_by=spawned_by_member,
        battle_begins_time=battle_begins_time,
    )

    if boss_name and "eternatus" in boss_name.lower():
        # Trigger CC bump reminder
        await send_cc_bump_reminder(
            bot=bot,
            context="spawned",
            variant=variant,
            timestamp=battle_begins_time,
        )
    else:
        # Trigger other wb reminder
        await send_cc_other_wb_reminder(
            bot=bot,
            boss_name=boss_name,
            variant=variant,
            timestamp=battle_begins_time,
        )


async def extract_boss_from_wb_command_embed(
    bot: commands.Bot, message: discord.Message
):
    """
    Extracts boss info from a WB embed message and triggers auto ping.
    Works even if there are emojis or extra text before the boss name.
    """
    try:
        for embed in message.embeds:
            description = embed.description
            if not description:
                continue

            # Remove all custom emojis for clean parsing
            clean_desc = re.sub(r"<:[\w\d]+:\d+>", "", description)

            # --- Extract boss name & variant ---
            boss_match = re.search(
                r"(Shiny\s+)?(?:Gigantamax|Eternamax)-([\w-]+)",
                clean_desc,
                re.IGNORECASE,
            )
            if boss_match:
                shiny_prefix, boss_name = boss_match.groups()
                variant = "shiny" if shiny_prefix else "regular"

                # Extract battle begins time
                battle_begins_time = extract_battle_begins_time_from_wb_command(
                    description
                )
                wb_command_user = await get_pokemeow_reply_or_interaction_member(
                    message
                )
                # Trigger auto ping
                await auto_wb_ping(
                    bot=bot,
                    message=message,
                    variant=variant,
                    boss=boss_name,
                    battle_begins_time=battle_begins_time,
                    wb_command_user=wb_command_user,
                )
                await check_ee_near_spawn_alert(bot=bot, message=message)
                if "eternatus" in boss_name.lower():
                    await send_cc_bump_reminder(
                        bot=bot,
                        context="wb spawn",
                        variant=variant,
                        timestamp=battle_begins_time,
                    )
                else:
                    await send_cc_other_wb_reminder(
                        bot=bot,
                        boss_name=boss_name,
                        variant=variant,
                        timestamp=battle_begins_time,
                    )
                return
    except Exception as e:
        pretty_log(
            "error",
            f"Failed to extract boss from embed: {e}",
        )
        return


async def auto_wb_ping(
    bot: commands.Bot,
    variant: str,
    boss: str,
    spawned_by: discord.Member = None,
    message: discord.Message = None,
    battle_begins_time: str | None = None,
    wb_command_user: discord.Member | None = None,
):
    """Auto posts a World Boss ping with proper cooldown, buttons, and logging."""
    guild = bot.get_guild(VNA_SERVER_ID)
    if not guild:
        pretty_log(
            "error",
            "Message has no guild!",
        )
        return

    # 🕒 Cooldown check
    cooldown_time = 300  # 5 minutes
    now = time.time()
    last_time = wb_shared_cooldowns.get(guild.id, 0)
    elapsed = now - last_time

    if elapsed < cooldown_time:
        pretty_log(
            "info",
            f"Auto WB ping blocked by shared cooldown ({int(cooldown_time - elapsed)}s remaining)",
        )
        return
    from utils.cache.active_wb_cache import fetch_active_wb_timestamp_and_boss

    timestamp_value = _parse_wb_timestamp(battle_begins_time)
    formatted_active_boss_name = boss
    if variant == "shiny":
        formatted_active_boss_name = f"shiny {boss}"
    if fetch_active_wb_timestamp_and_boss():
        wb_timestamp, wb_boss = fetch_active_wb_timestamp_and_boss()
        if (
            wb_boss
            and wb_boss.lower() == formatted_active_boss_name.lower()
            and timestamp_value is not None
            and timestamp_value == wb_timestamp
        ):
            pretty_log("info", f"Auto WB ping blocked: {boss} is already active.")
            return

    # ✅ Update the shared cooldown
    wb_shared_cooldowns[guild.id] = now

    # 🗺️ Remap aliases
    remap = {
        "uss": "uss",
        "urshifu-singlestrike": "uss",
        "urs": "urs",
        "urshifu-rapidstrike": "urs",
        "ee": "eternatus",
    }
    lower_boss = boss.lower()
    key = remap.get(lower_boss, lower_boss)

    footer_text = f"Post made by {bot.user.name}"
    if wb_command_user:
        footer_text = f"Post made by {wb_command_user.display_name}"
    if spawned_by:
        footer_text = f"Spawned by {spawned_by.display_name}"

    upper_boss = boss.upper()
    reg_link = "https://discord.com/channels/664509279251726363/682412861926014976"
    start_timestamp_line = ""
    pretty_log(
        "info",
        f"Battle begins time extracted: {battle_begins_time}",
    )
    if battle_begins_time and battle_begins_time.isdigit():
        start_timestamp_line = f"- **Battle Begins ** <t:{battle_begins_time}:R>\n"

    try:
        # 🧠 Define boss metadata
        if key == "eternatus":
            if variant == "regular":
                boss_name = "ETERNAMAX-ETERNATUS"
                color = WBColors.eternatus
                image = WBRegImage.eternatus
                content = f"{WBEmojis.WB_Spawn} {guild.get_role(VN_ALLSTARS_ROLES.ee_spawn_ping).mention} {guild.get_role(VN_ALLSTARS_ROLES.world_boss_spawn).mention} EMAX-ETERNATUS"
            else:
                boss_name = "SHINY ETERNAMAX-ETERNATUS"
                color = WBColors.Shiny
                image = WBShinyImage.eternatus
                content = f"{WBEmojis.WB_Spawn} {guild.get_role(VN_ALLSTARS_ROLES.ee_spawn_ping).mention} {guild.get_role(VN_ALLSTARS_ROLES.world_boss_spawn).mention} SEMAX-ETERNATUS"
        else:
            boss_name = (
                "URSHIFU-SINGLESTRIKE"
                if key == "uss"
                else (
                    "URSHIFU-RAPIDSTRIKE"
                    if key == "urs"
                    else (
                        f"SHINY GIGANTAMAX-{upper_boss}"
                        if variant == "shiny"
                        else f"GIGANTAMAX-{upper_boss}"
                    )
                )
            )
            color = (
                WBColors.Shiny
                if variant == "shiny"
                else getattr(WBColors, key, discord.Color.greyple())
            )
            image = getattr(
                WBShinyImage if variant == "shiny" else WBRegImage, key, None
            )
            content = f"{WBEmojis.WB_Spawn} {guild.get_role(VN_ALLSTARS_ROLES.world_boss_spawn).mention} {boss_name}"

        # 📦 Create Embed
        embed = discord.Embed(
            title=f"{WBEmojis.WB_Spawn} A WORLD BOSS HAS SPAWNED!",
            description=(
                f"**COME JOIN THE BATTLE!**\n"
                f"- **REGISTER:** `;wb`\n"
                f"- **BOSS:** {WBEmojis.Sgmax if variant=='shiny' else WBEmojis.Gmax} {boss_name}\n"
                f"- **GUIDE:** `{getattr(WBGuide, key, 'No guide available.')}`\n"
                f"{start_timestamp_line}"
                f"For more info: Use command `!wb` or `!wbi`\n\n"
                # f"To get pings for a specific wb: Use `/wb-sub add`"
            ),
            color=color,
        )
        if image:
            embed.set_image(url=image)
        embed.set_footer(text=footer_text, icon_url=guild.icon.url)

        # 🎛️ Buttons
        view = discord.ui.View(timeout=300)
        if key == "eternatus":
            view.add_item(
                WBRoleToggleButton(
                    "Toggle EE Ping", VN_ALLSTARS_ROLES.ee_spawn_ping, emoji=WB_REGEMOJI.eet
                )
            )
        view.add_item(
            WBRoleToggleButton(
                "Toggle WB Spawn Ping",
                VN_ALLSTARS_ROLES.world_boss_spawn,
                emoji=WBEmojis.WB_Spawn,
            )
        )

        # 📤 Send message
        channel = guild.get_channel(VN_ALLSTARS_TEXT_CHANNELS.world_boss_spawn)
        if not channel:
            pretty_log(
                "error",
                f"WB Tracker channel not found in guild {guild.name}",
            )
            return
        await cleanup_first_match(
            bot=bot, channel=channel, phrase="Post made by", component="footer"
        )
        wb_msg = await channel.send(content=content, embed=embed, view=view)
        pretty_log(
            "success",
            f"Auto WB ping posted for {boss_name}",
        )

        if message:
            await message.add_reaction(PLUS_EMOJI)

        # Update active wb
        if timestamp_value is not None:
            await upsert_active_wb(
                bot=bot,
                boss_name=formatted_active_boss_name,
                wb_timestamp=timestamp_value,
            )

    except Exception as e:
        pretty_log(
            "error",
            f"Failed auto WB ping: {e}",
        )


class WBRoleToggleButton(discord.ui.Button):
    def __init__(self, label: str, role_id: int, emoji: str = None):
        super().__init__(label=label, emoji=emoji, style=discord.ButtonStyle.secondary)
        self.role_id = role_id

    async def callback(self, interaction: discord.Interaction):
        try:
            role = interaction.guild.get_role(self.role_id)
            if not role:
                return await interaction.response.send_message(
                    "❌ Role not found.", ephemeral=True
                )

            if role in interaction.user.roles:
                await interaction.user.remove_roles(role)
                await interaction.response.send_message(
                    f"❌ Removed {role.mention}.", ephemeral=True
                )
            else:
                await interaction.user.add_roles(role)
                await interaction.response.send_message(
                    f"✅ Added {role.mention}.", ephemeral=True
                )
        except Exception as e:
            pretty_log(
                "error",
                f"Role toggle failed: {e}",
            )


async def remove_buttons_after_delay(message: discord.Message, delay=300):
    try:
        await asyncio.sleep(delay)
        await message.edit(view=None)
    except Exception as e:
        pretty_log(
            "error",
            f"Failed to remove buttons: {e}",
        )


# -------------------- Persistent cache --------------------
CACHE_FILE = "Data/ee_votes_cache.json"
last_seen_votes = {}
near_spawn_alert_cache = set()


def load_vote_cache():
    global last_seen_votes, near_spawn_alert_cache
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                last_seen_votes = data.get("last_seen_votes", {})
                near_spawn_alert_cache = set(data.get("near_spawn_alert_cache", []))
                pretty_log(
                    "cache",
                    "Loaded EE vote cache from file",
                )
        except Exception as e:
            pretty_log(
                "error",
                f"Failed to load EE vote cache: {e}",
            )
            last_seen_votes = {}
            near_spawn_alert_cache = set()
    else:
        last_seen_votes = {}
        near_spawn_alert_cache = set()


def save_vote_cache():
    try:
        data = {
            "last_seen_votes": last_seen_votes,
            "near_spawn_alert_cache": list(near_spawn_alert_cache),
        }
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        pretty_log(
            "error",
            f"Failed to save EE vote cache: {e}",
        )


# -------------------- EE Near Spawn Checker --------------------
async def check_ee_near_spawn_alert(bot: commands.Bot, message: discord.Message):
    """
    Checks WB embeds for Eternamax-Eternatus vote counts.
    Sends an alert in WB tracker channel when votes left <= 100.
    Resets alert once votes drop (new spawn).
    Also logs current cache every time.
    """
    try:
        for embed in message.embeds:
            description = embed.description
            if not description:
                pretty_log(
                    "warn",
                    f"Skipping embed {message.id}: no description",
                )
                continue

            # Remove all custom emojis & trim whitespace
            clean_desc = re.sub(r"<:[\w\d]+:\d+>", "", description).strip()

            # Match Eternamax-Eternatus spawn line
            vote_match = re.search(
                r"Eternamax-Eternatus\s+spawn:\s*([\d,]+)\s*/\s*([\d,]+)",
                clean_desc,
                re.IGNORECASE,
            )
            if not vote_match:
                pretty_log(
                    "info",
                    f"Skipping embed {message.id}: no Eternamax-Eternatus spawn line found",
                )
                continue

            current_votes, total_votes = vote_match.groups()
            current_votes = int(current_votes.replace(",", ""))
            total_votes = int(total_votes.replace(",", ""))
            votes_left = total_votes - current_votes

            boss_key = "eternamax-eternatus"

            # Reset alert if votes decreased (new spawn)
            prev_votes = int(last_seen_votes.get(boss_key, 0))
            if current_votes < prev_votes:
                near_spawn_alert_cache.discard(boss_key)
                pretty_log(
                    "info",
                    f"Votes decreased for {boss_key}, resetting alert cache",
                )

            last_seen_votes[boss_key] = current_votes
            save_vote_cache()  # save after updating votes

            # Only alert once per spawn when votes left <= 100
            if votes_left <= 100 and boss_key not in near_spawn_alert_cache:
                near_spawn_alert_cache.add(boss_key)
                save_vote_cache()  # save after sending alert

                channel_id = VN_ALLSTARS_TEXT_CHANNELS.world_boss_spawn
                ee_ping_role_id = VN_ALLSTARS_ROLES.ee_spawn_ping

                channel = bot.get_channel(channel_id) or Object(id=channel_id)
                await channel.send(
                    f"<@&{ee_ping_role_id}> ⚠️ Only {votes_left} votes left until Eternamax-Eternatus spawns!"
                )

                pretty_log(
                    "ready",
                    f"Sent near-spawn alert for {boss_key}: {current_votes}/{total_votes} votes",
                )

                # Trigger CC bump reminder
                await send_cc_bump_reminder(
                    bot=bot,
                    context="votes left",
                    votes_left=str(votes_left),
                )
            else:
                pretty_log(
                    "info",
                    f"Skipping alert for {boss_key}: votes_left={votes_left}, already alerted={boss_key in near_spawn_alert_cache}",
                )

            # --- Log current cache for debugging ---
            pretty_log(
                "info",
                f"Current EE cache: last_seen_votes={last_seen_votes}, near_spawn_alert_cache={near_spawn_alert_cache}",
            )

            # Stop after first match
            return

    except Exception as e:
        pretty_log(
            "error",
            f"Failed near-spawn check for Eternamax-Eternatus: {e}",
        )

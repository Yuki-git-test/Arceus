import json
import os
import re
import time

import discord
from discord import Object
from discord.ext import commands

from Constants.variables import CC_BUMP_CHANNEL_ID, CC_GUILD_ID
from Constants.vn_allstars_constants import (
    ARCEUS_EMBED_COLOR,
    VN_ALLSTARS_EMOJIS,
    VN_ALLSTARS_ROLES,
    VN_ALLSTARS_TEXT_CHANNELS,
    VNA_SERVER_ID,
)
from utils.logs.debug_log import debug_log, enable_debug
from utils.logs.pretty_log import pretty_log

Reg_EE = "https://play.pokemonshowdown.com/sprites/xyani/eternatus-eternamax.gif"
Shiny_EE = "https://play.pokemonshowdown.com/sprites/ani-shiny/eternatus-eternamax.gif"
REG_EE_COLOR = 4077189
SHINY_EE_COLOR = 16561340


enable_debug(f"{__name__}.check_cc_bump_reminder")
# ⏳ Shared cooldowns across commands/listeners
wb_shared_cooldowns: dict[int, float] = {}  # {guild_id: last_post_time}
cc_shared_cooldowns: dict[int, float] = {}  # {guild_id: last_post_time}
# -------------------- Persistent cache --------------------
CACHE_FILE = "Data/ee_votes_cache.json"

last_seen_votes = {}
near_spawn_alert_cache = set()

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


def extract_timestamp_from_wb_spawn_command(description: str):
    match = re.search(r"Challenge starts <t:(\d+):R>", description)
    if match:
        return match.group(1).strip()
    return None


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


async def check_cc_bump_reminder(bot: commands.Bot, message: discord.Message):
    debug_log(
        f"Called for message.id: {getattr(message, 'id', None)} | bot: {getattr(bot, 'user', None)}"
    )
    embed = message.embeds[0] if message.embeds else None
    debug_log(f"Embed: {embed}")
    if not embed:
        debug_log("No embed found, exiting.")
        return

    if message.author.id == bot.user.id:
        debug_log("Message sent by bot, exiting.")
        return

    embed_title = embed.title or ""
    embed_description = embed.description or ""
    debug_log(f"Embed title: {embed_title}")
    debug_log(f"Embed description: {embed_description}")

    if embed_title == "Votes left until EE Spawn":
        boss_key = "eternamax-eternatus"
        votes_left = embed_description.strip()
        debug_log(f"Votes left: {votes_left}")
        last_seen_votes[boss_key] = votes_left
        votes_left_int = int(votes_left.replace(",", ""))  # Handles numbers with commas
        debug_log(f"votes_left_int: {votes_left_int}")
        if votes_left_int <= 100 and boss_key not in near_spawn_alert_cache:
            debug_log(f"Alert condition met for {boss_key}.")
            near_spawn_alert_cache.add(boss_key)
            save_vote_cache()  # save after sending alert
            vna_guild = bot.get_guild(VNA_SERVER_ID)
            debug_log(f"vna_guild: {vna_guild}")
            channel_id = VN_ALLSTARS_TEXT_CHANNELS.bumps
            ee_ping_role_id = VN_ALLSTARS_ROLES.ee_spawn_ping

            channel = vna_guild.get_channel(channel_id) or Object(id=channel_id)
            debug_log(f"Sending alert to channel: {channel}")
            await channel.send(
                f"<@&{ee_ping_role_id}> ⚠️ Only {votes_left} votes left until Eternamax-Eternatus spawns!"
            )

            pretty_log(
                "ready",
                f"Sent near-spawn alert for {boss_key}: {votes_left} votes left from cc  bump reminder",
            )
            await message.add_reaction(PLUS_EMOJI)
        else:
            debug_log(f"Alert condition not met or already alerted for {boss_key}.")
    elif "EE Spawned" in embed_title:
        timestamp = embed_description.strip()
        debug_log(f"EE Spawned detected, timestamp: {timestamp}")
        await auto_wb_ping(
            bot=bot,
            variant="shiny" if "Shiny" in embed_title else "regular",
            boss="eternatus",
            battle_begins_time=timestamp,
            source="cc_bump_reminder",
        )
    await message.add_reaction(CHECK_EMOJI)


async def send_cc_bump_reminder(
    bot: commands.Bot,
    context: str,
    votes_left: str = None,
    variant: str = "regular",
    timestamp: str = None,
    source: str = "server",
):

    cc_guild = bot.get_guild(CC_GUILD_ID)
    cc_bump_channel = cc_guild.get_channel(CC_BUMP_CHANNEL_ID)
    if context == "votes left" and votes_left:
        title = "Votes left until EE Spawn"
        description = votes_left
        color = ARCEUS_EMBED_COLOR

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
        if variant == "shiny":
            title = "Shiny EE Spawned"
            color = SHINY_EE_COLOR
        else:
            title = "EE Spawned"
            color = REG_EE_COLOR

        # Cooldown check
        cooldown_time = 300  # 5 minutes
        now = time.time()
        last_time = cc_shared_cooldowns.get(VNA_SERVER_ID, 0)
        elapsed = now - last_time
        if elapsed < cooldown_time:
            pretty_log(
                "info",
                f"CC bump reminder blocked by shared cooldown ({int(cooldown_time - elapsed)}s remaining)",
            )
            return
        # ✅ Update the shared cooldown
        cc_shared_cooldowns[VNA_SERVER_ID] = now

        bump_embed = discord.Embed(title=title, description=description, color=color)

        if source == "server":
            await cc_bump_channel.send(embed=bump_embed)
            pretty_log(
                "success",
                f"Sent CC bump reminder for ee spawn in {cc_bump_channel.name}",
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

                channel_id = VN_ALLSTARS_TEXT_CHANNELS.bumps
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


# ⏳ Keep track of cooldown per guild (shared with slash command ideally)
guild_cooldowns: dict[int, float] = {}  # {guild_id: last_post_time}


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
            else:
                return  # Exit if not eternatus spawn

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

    # Trigger auto ping only for etrnamax-eternatus
    if boss_name and boss_name.lower() == "eternatus":
        await auto_wb_ping(
            bot=bot,
            variant=variant,
            boss=boss_name,
            spawned_by=spawned_by_member,
            battle_begins_time=battle_begins_time,
        )
        # Trigger CC bump reminder
        """await send_cc_bump_reminder(
            bot=bot,
            context="spawned",
            variant=variant,
            timestamp=battle_begins_time,
        )
    """


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

            # Extract battle begins time
            battle_begins_time = extract_battle_begins_time_from_wb_command(description)

            if boss_match:
                shiny_prefix, boss_name = boss_match.groups()
                variant = "shiny" if shiny_prefix else "regular"

                # Trigger auto ping only for etrnamax-eternatus
                if boss_name.lower() == "eternatus":
                    await auto_wb_ping(bot=bot, variant=variant, boss=boss_name)

                return
    except Exception as e:
        pretty_log(
            "error",
            f"Failed to extract boss from embed: {e}",
        )
        return


EE_SETTING_MAP = {
    "regular": {
        "image_url": Reg_EE,
        "color": REG_EE_COLOR,
    },
    "shiny": {
        "image_url": Shiny_EE,
        "color": SHINY_EE_COLOR,
    },
}


async def auto_wb_ping(
    bot: commands.Bot,
    variant: str,
    boss: str,
    spawned_by: discord.Member | None = None,
    battle_begins_time: str | None = None,
    message: discord.Message | None = None,
    source: str = "server",
):

    # 🕒 Cooldown check
    cooldown_time = 300  # 5 minutes
    guild: discord.Guild = bot.get_guild(VNA_SERVER_ID)
    now = time.time()
    last_time = wb_shared_cooldowns.get(guild.id, 0)
    elapsed = now - last_time

    if elapsed < cooldown_time:
        pretty_log(
            "info",
            f"Auto WB ping blocked by shared cooldown ({int(cooldown_time - elapsed)}s remaining)",
        )
        return

    # ✅ Update the shared cooldown
    wb_shared_cooldowns[guild.id] = now

    channel_id = VN_ALLSTARS_TEXT_CHANNELS.bumps
    ee_ping_role_id = VN_ALLSTARS_ROLES.ee_spawn_ping
    channel = guild.get_channel(channel_id)
    ee_ping_role = guild.get_role(ee_ping_role_id)

    variant_emoji = (
        VN_ALLSTARS_EMOJIS.vna_shinygmax
        if variant == "shiny"
        else VN_ALLSTARS_EMOJIS.vna_gmax
    )
    boss_name = "Eternamax-Eternatus"
    color = EE_SETTING_MAP[variant]["color"]
    image_url = EE_SETTING_MAP[variant]["image_url"]
    start_timestamp_line = ""
    if (
        battle_begins_time
        and battle_begins_time.isdigit()
        and battle_begins_time != "N/A"
    ):
        start_timestamp_line = f"- **Battle Begins** <t:{battle_begins_time}:R>\n"

    content = f"<@&{ee_ping_role_id}>"
    if variant == "shiny":
        content = f"Shiny <@&{ee_ping_role_id}>"

    reg_link = "https://discord.com/channels/664509279251726363/682412861926014976"
    embed = discord.Embed(
        title=f"A WORLD BOSS HAS SPAWNED!",
        description=(
            f"**COME JOIN THE BATTLE!**\n"
            f"- **REGISTER:** {reg_link}\n"
            f"- **BOSS:** {variant_emoji} {boss_name}\n"
            f"{start_timestamp_line}"
        ),
        color=color,
    )
    if spawned_by:
        footer_text = f"Spawned by {spawned_by.display_name}"
        embed.set_footer(text=footer_text)
    embed.set_image(url=image_url)

    await channel.send(content=content, embed=embed)
    pretty_log(
        "success",
        f"Sent auto WB ping for {variant} {boss_name} in {channel.name}",
    )

    # Trigger CC bump reminder
    await send_cc_bump_reminder(
        bot=bot,
        context="spawned",
        variant=variant,
        timestamp=battle_begins_time,
        source=source,
    )
    if message:
        await message.add_reaction(PLUS_EMOJI)

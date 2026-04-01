import re
import time

import discord

from Constants.vn_allstars_constants import VN_ALLSTARS_TEXT_CHANNELS
from utils.db.berry_reminder import (
    berry_map,
    fetch_user_all_berry_reminder,
    get_user_berry_reminder_slot,
    update_moisture_dries_on,
    update_mulch_info,
    upsert_berry_reminder,
)
from utils.logs.debug_log import debug_log, enable_debug
from utils.logs.pretty_log import pretty_log
from utils.pokemeow.get_pokemeow_reply import get_pokemeow_reply_member

enable_debug(f"{__name__}.handle_berry_water_message")
enable_debug(f"{__name__}.handle_growth_mulch_message")


def parse_berry_water_message(message: str):
    """
    Extracts slot_number, berry_name, stage, grows_on for each berry in a berry water message.
    Also extracts the emoji name of the watering can used, if present at the top of the message.
    Returns a dict with keys: 'watering_can_emoji', 'berries' (list of dicts, one per berry).
    """
    import re

    # Extract watering can emoji name from the first line
    watering_can_emoji = None
    first_line = message.splitlines()[0] if message.splitlines() else ""
    emoji_match = re.search(r"<:([a-zA-Z0-9_]+):\d+>", first_line)
    if emoji_match:
        watering_can_emoji = emoji_match.group(1)
        watering_can_emoji = watering_can_emoji.lower().replace("_", " ")

    results = []
    # Split by "Slot" to isolate each berry block
    for block in re.split(r"(?=Slot \d+)", message):
        slot_match = re.search(r"Slot (\d+)", block)
        if not slot_match:
            continue
        slot_number = int(slot_match.group(1))

        # Berry name
        berry_match = re.search(r"\*\*([A-Za-z ]+ Berry)\*\*", block)
        berry_name = berry_match.group(1).strip() if berry_match else None

        # Stage
        stage_match = re.search(r"• <:[^:]+:\d+> \*\*([A-Za-z ]+)\*\*", block)
        stage = stage_match.group(1).strip() if stage_match else None

        # Grows on (unix seconds)
        grows_on_match = re.search(r"at <t:(\d+):F>", block)
        grows_on = int(grows_on_match.group(1)) if grows_on_match else None

        results.append(
            {
                "slot_number": slot_number,
                "berry_name": berry_name,
                "stage": stage,
                "grows_on": grows_on,
            }
        )

    return {"watering_can_emoji": watering_can_emoji, "berries": results}


async def handle_berry_water_message(bot: discord.Client, message: discord.Message):

    debug_log(f"Handling berry water message: {message.content}")
    member = await get_pokemeow_reply_member(message)
    if not member:
        debug_log("No member found in pokemeow reply.")
        return
    user_id = member.id
    guild = message.guild

    parsed_data = parse_berry_water_message(message.content)
    if not parsed_data or not parsed_data.get("berries"):
        debug_log("Message did not match berry water format.")
        return
    debug_log(f"Parsed berry water message: {parsed_data}")

    from utils.cache.vna_members_cache import fetch_vna_member_channel_id_from_cache

    member_channel_id = (
        fetch_vna_member_channel_id_from_cache(user_id)
        if fetch_vna_member_channel_id_from_cache(user_id)
        else VN_ALLSTARS_TEXT_CHANNELS.off_topic
    )

    member_channel = guild.get_channel(member_channel_id) if member_channel_id else None
    member_channel_name = member_channel.name if member_channel else None

    user_name = member.name

    # Upsert each berry reminder in the database
    for berry in parsed_data["berries"]:
        try:
            # Compute moisture dries on based on berry
            moisture_dries_on = None
            water_can_type = parsed_data["watering_can_emoji"]
            if water_can_type != "sprayduck":
                berry_name = (
                    berry["berry_name"].lower() if berry["berry_name"] else None
                )
                debug_log(f"Looking up berry info for {berry_name}")
                berry_info = berry_map.get(berry_name)

                if berry_info:
                    moisture_dries_on_duration = berry_info["moisture_dry_out_duration"]
                    # compute current time + moisture dries on in seconds
                    moisture_dries_on = int(time.time()) + moisture_dries_on_duration

            await upsert_berry_reminder(
                bot,
                user_id=user_id,
                user_name=user_name,
                slot_number=berry["slot_number"],
                grows_on=berry["grows_on"],
                stage=berry["stage"],
                channel_id=member_channel_id,
                channel_name=member_channel_name,
                berry_name=berry["berry_name"],
                water_can_type=parsed_data["watering_can_emoji"],
                moisture_dries_on=moisture_dries_on,
            )
            pretty_log(
                "db",
                f"Upserted berry reminder for {user_name} (user_id: {user_id}) in slot {berry['slot_number']}, reminds on {berry['grows_on']}, stage: {berry['stage']}",
            )
        except Exception as e:
            pretty_log(
                "warn",
                f"Failed to upsert berry reminder for user {user_id} in slot {berry['slot_number']}: {e}",
            )

    # Add reaction to the replied message (if any)
    replied_message = message.reference and message.reference.resolved
    if replied_message:
        reaction_emoji = "✅"
        try:
            await replied_message.add_reaction(reaction_emoji)
            debug_log(
                f"Added reaction {reaction_emoji} to message ID {replied_message.id}"
            )
        except Exception as e:
            debug_log(f"Failed to add reaction to message ID {replied_message.id}: {e}")


async def handle_mulch_message(bot, message):
    debug_log(f"Handling mulch message: {message.content}")
    member = await get_pokemeow_reply_member(message)
    if not member:
        debug_log("No member found in pokemeow reply.")
        return
    user_id = member.id
    guild = message.guild

    send_message = True
    if "growth mulch" in message.content.lower():

        content = f"{member.mention} please use `;berry` so I can update your next berry stage reminder!"
    else:
        mulch_info = extract_mulch_info_message(message.content)
        if not mulch_info:
            return
        debug_log(f"Extracted mulch info: {mulch_info}")
        slot_number = mulch_info["slot_number"]
        mulch_type = mulch_info["mulch_type"]
        # Check if slot number exists for this user in the database
        existing_reminder = await get_user_berry_reminder_slot(
            bot, user_id, slot_number
        )
        if existing_reminder:
            await update_mulch_info(bot, user_id, slot_number, mulch_type)
            send_message = False
            if "damp mulch" in message.content.lower():
                berry_data = await get_user_berry_reminder_slot(
                    bot, user_id, slot_number
                )
                berry_name = berry_data["berry_name"] if berry_data else "unknown berry"
                berry_name = berry_name.lower() if berry_name else "unknown berry"
                berry_info = berry_map.get(berry_name)
                if berry_info:
                    moisture_dries_on_duration = berry_info["moisture_dry_out_duration"]
                    moisture_dries_on_time = berry_data["moisture_dries_on"]
                    if moisture_dries_on_time and moisture_dries_on_duration:
                        new_moisture_dries_on = (
                            moisture_dries_on_time + moisture_dries_on_duration
                        )
                        await update_moisture_dries_on(
                            bot, user_id, slot_number, new_moisture_dries_on
                        )
                        pretty_log(
                            "db",
                            f"Updated moisture dries on for user_id {user_id} slot {slot_number} to {new_moisture_dries_on} after damp mulch application.",
                        )

        else:
            content = f"{member.mention} I noticed you applied {mulch_type} to slot {slot_number}, but I couldn't find that slot in my database. Please use `;berry` so I can update your reminders!"

    if send_message:
        await message.channel.send(content)


def extract_mulch_info_message(message: str):
    """
    Extracts the mulch type and slot number from a mulch application message.
    Returns a dict with keys: 'mulch_type' and 'slot_number', or None if not found.
    """
    import re

    # Example: <:gooey_mulch:1486261017691557919> Applied **Gooey Mulch** to Slot 3 (<:planted:1486510464417402960> Hondew Tree)!
    pattern = re.compile(
        r"<:([a-zA-Z0-9_]+):\d+> Applied \*\*([A-Za-z ]+)\*\* to Slot (\d+)",
        re.IGNORECASE,
    )
    match = pattern.search(message)
    if match:
        emoji_name = match.group(1)
        mulch_type = match.group(2).strip()
        slot_number = int(match.group(3))
        return {
            "mulch_type": mulch_type,
            "slot_number": slot_number,
            "emoji_name": emoji_name,
        }
    return None

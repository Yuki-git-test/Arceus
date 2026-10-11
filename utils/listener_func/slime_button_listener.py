
import discord

from utils.cache.cache_list import processed_slime_button_messages
from utils.db.user_alerts_db import fetch_user_alert_notify, upsert_user_alert
from utils.logs.debug_log import debug_log, enable_debug
from utils.pokemeow.get_pokemeow_reply import \
    get_pokemeow_reply_or_interaction_member

enable_debug(f"{__name__}.slime_button_listener")



async def slime_button_listener(bot:discord.Client, message:discord.Message):
    debug_log(
        f"Slime button listener triggered: message_id={message.id}, "
        f"channel_id={message.channel.id}"
    )

    if message.id in processed_slime_button_messages:
        debug_log(f"Skipping already processed message: {message.id}")
        return
    processed_slime_button_messages.add(message.id)
    debug_log(f"Marked message as processed: {message.id}")

    # Get member object
    member = await get_pokemeow_reply_or_interaction_member(message)
    debug_log(f"Resolved member: {member!r}")
    if not member:
            return

    user_id = member.id
    debug_log(f"Resolved member ID: {user_id}")
    if not user_id:
        debug_log("Resolved member has no user ID; returning")
        return

    # Check user slime notification setting
    user_slime_notify = await fetch_user_alert_notify(bot, user_id, "slime")
    debug_log(f"Slime alert lookup for user {user_id}: {user_slime_notify!r}")

    if not user_slime_notify:
        # Upsert with default on_no_pings
        debug_log(f"No slime alert found for user {user_id}; creating on_no_pings alert")
        await upsert_user_alert(bot, user_id, member.name, "slime", "on_no_pings")
        user_slime_notify = "on_no_pings"
        debug_log(f"Created default slime alert for user {user_id}")

    debug_log(f"User slime notify setting: {user_slime_notify}")
    if user_slime_notify.lower() == "off":
        debug_log("User slime notify setting is off, returning early")
        return

    if user_slime_notify.lower() == "on":
        user_ = member.mention
    elif user_slime_notify.lower() == "on_no_pings":
        user_ = f"**{member.name}**"
    else:
        debug_log(f"Unknown slime notify setting {user_slime_notify!r} for user {user_id}, returning early")
        return
    remind_message = f"🪣 {user_} Click the claim slime button!"

    await message.channel.send(remind_message)



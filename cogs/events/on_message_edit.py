import re
from datetime import datetime, timezone

import discord
from discord.ext import commands

from Constants.variables import POKEMEOW_APPLICATION_ID
from utils.listener_func.berry_listener import berry_listener
from utils.listener_func.berry_pouch_listener import handle_berry_pouch_message
from utils.listener_func.explore_caught_listener import explore_caught_listener
from utils.listener_func.fish_spawn_listener import fish_spawn_listener
from utils.listener_func.monthly_stats_listener import monthly_stats_listener
from utils.listener_func.pin_timer_listener import pin_timer_listener
from utils.listener_func.pokemon_caught_listener import pokemon_caught_listener
from utils.listener_func.pokemon_pin_numbers_listener import \
    pokemon_pin_numbers_listener
from utils.listener_func.slime_button_listener import slime_button_listener
from utils.listener_func.wb_reg_listener import handle_wb_register_command
from utils.listener_func.weekly_stats_listener import weekly_stats_listener
from utils.logs.pretty_log import pretty_log

# ️────────────────────────────────────────────
#        ⚔️ Message Triggers
# ️────────────────────────────────────────────
triggers = {
    "weekly_stats_command": "**Clan Weekly Stats — VN Allstar**",
    "monthly_stats_command": "**Clan Monthly Stats — VN Allstar**",
    "explore_listener": "⏱️ Your explore session has ended!",
    "caught_listener": "You caught",
}

# Guard against duplicate edit dispatches for the same message payload.
_recent_edit_signatures: dict[tuple[int, str], datetime] = {}
_EDIT_DEDUP_TTL_SECONDS = 180

def _iter_message_buttons(message: discord.Message):
    """Yield all button components, guarding against partial edit payloads
    where the components slot was never set (AttributeError risk)."""
    for row in getattr(message, "components", None) or []:
        for component in getattr(row, "children", None) or []:
            if component.type != discord.ComponentType.button:
                continue
            yield component


def has_slime_button(message: discord.Message) -> bool:
    """Returns True if the message has a button with 'slime' in its label, emoji, or custom ID."""
    for button in _iter_message_buttons(message):
        label = (button.label or "").lower()
        emoji = getattr(button, "emoji", None)
        emoji_name = (getattr(emoji, "name", "") or "").lower()
        custom_id = (getattr(button, "custom_id", "") or "").lower()
        if "slime" in label or "slime" in emoji_name or "slime" in custom_id:
            return True
    return False

def get_number_after_exclamation(text):
    match = re.search(r'!\s*(\d+)', text)
    return match.group(1) if match else None

def _build_component_signature(message: discord.Message) -> str:
    """Build a signature from message components so component-only edits are detected."""
    parts = []
    for row in getattr(message, "components", None) or []:
        for component in getattr(row, "children", None) or []:
            label = getattr(component, "label", None) or ""
            emoji = getattr(component, "emoji", None)
            emoji_name = (getattr(emoji, "name", "") or "") if emoji else ""
            custom_id = getattr(component, "custom_id", None) or ""
            parts.append(f"{component.type.value}:{label}:{emoji_name}:{custom_id}")
    return ",".join(parts)


def _build_edit_signature(message: discord.Message) -> str:
    """Build a stable signature from content + first embed fields used by listeners."""
    content = message.content or ""
    components = _build_component_signature(message)
    first_embed = message.embeds[0] if message.embeds else None
    if not first_embed:
        return "|".join([content, components])

    author = first_embed.author.name if first_embed.author else ""
    title = first_embed.title or ""
    description = first_embed.description or ""
    footer = first_embed.footer.text if first_embed.footer else ""
    return "|".join([content, author, title, description, footer, components])


# 🍭──────────────────────────────
#   🎀 Event: On Message Edit
# 🍭──────────────────────────────
class OnMessageEditCog(commands.Cog):
    """Cog to handle message edit events."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):

        before_sig = _build_edit_signature(before)
        after_sig = _build_edit_signature(after)
        if before_sig == after_sig:
            return

        now_utc = datetime.now(timezone.utc)
        stale_keys = [
            k
            for k, seen_at in _recent_edit_signatures.items()
            if (now_utc - seen_at).total_seconds() > _EDIT_DEDUP_TTL_SECONDS
        ]
        for k in stale_keys:
            _recent_edit_signatures.pop(k, None)

        dedup_key = (after.id, after_sig)
        if dedup_key in _recent_edit_signatures:
            pretty_log(
                "debug",
                f"Skipped duplicate on_message_edit processing for message_id={after.id}",
                label="MESSAGE",
                bot=self.bot,
            )
            return
        _recent_edit_signatures[dedup_key] = now_utc

        # Ignore edits made by bots except PokéMeow
        if after.author.bot and after.author.id != POKEMEOW_APPLICATION_ID:
            return

        # Partial edit payloads (e.g. PokéMeow adding the slime button via a
        # component-only update) omit embeds/content, so fall back to the
        # cached before message for those fields.
        content = after.content or before.content or ""
        first_embed = (
            after.embeds[0]
            if after.embeds
            else (before.embeds[0] if before.embeds else None)
        )
        first_embed_author_text = (
            first_embed.author.name if first_embed and first_embed.author else ""
        )
        first_embed_description = first_embed.description if first_embed else ""
        first_embed_footer_text = (
            first_embed.footer.text if first_embed and first_embed.footer else ""
        )
        first_embed_title = first_embed.title if first_embed else ""

        # ————————————————————————————————
        # 🩵 Guild Check — Skip DMs (runs in all guilds)
        # ————————————————————————————————
        if not after.guild:
            return
        # ————————————————————————————————
        # 🩵 Berry Command Listener
        # ————————————————————————————————
        if first_embed:
            if (
                first_embed_description
                and "garden overview" in first_embed_description.lower()
            ):
                pretty_log(
                    "info",
                    "Detected Garden Overview embed, processing berry reminders...",
                )
                await berry_listener(
                    bot=self.bot,
                    before_message=before,
                    message=after,
                )
        # ————————————————————————————————
        # 🩵 VNA Berry Pouch Listener
        # ————————————————————————————————
        if first_embed:
            if (
                first_embed_footer_text
                and "berry pouch" in first_embed_footer_text.lower()
            ):
                pretty_log(
                    "info",
                    "Detected Berry Pouch embed, processing berry pouch listener...",
                )
                await handle_berry_pouch_message(
                    bot=self.bot,
                    before=before,
                    message=after,
                )
        # ————————————————————————————————
        # 🩵 VNA Fish Spawn Listener
        # ————————————————————————————————
        if (
            first_embed_description
            and "fished a wild" in first_embed_description.lower()
        ):
            await fish_spawn_listener(self.bot, before, after)
        # ————————————————————————————————
        # ⚡ Fish Pin Alert
        # ————————————————————————————————
        if after.embeds:
           if first_embed_author_text and "a wild pokemon appeared" in first_embed_author_text.lower():
               pin_number = get_number_after_exclamation(first_embed_author_text)
               if pin_number:
                   await pokemon_pin_numbers_listener(
                       bot=self.bot,
                       message=after,
                       pin_number=pin_number,
                       source="fish",
                   )

        # ————————————————————————————————
        # 🩵 Pokemon Caught Listener (Weekly/Monthly Goal Tracker + Slime Button)
        # ————————————————————————————————
        if first_embed:
            if triggers["caught_listener"] in first_embed_description:
                slime_button = has_slime_button(after) or has_slime_button(before)
                await pokemon_caught_listener(self.bot, before, after)
                if slime_button:
                    pretty_log(
                        "info",
                        f"Detected slime button in Pokemon Caught embed for message ID: {after.id}",
                    )
                    # Component-only partial edits lack reference/interaction data
                    # needed for member resolution, so use the cached before message.
                    slime_message = after if after.embeds else before
                    await slime_button_listener(self.bot, slime_message)
                else:
                    pretty_log(
                        "debug",
                        f"Pokemon Caught edit without slime button | message_id={after.id} | "
                        f"after_components=[{_build_component_signature(after)}] | "
                        f"before_components=[{_build_component_signature(before)}]",
                        label="MESSAGE",
                        bot=self.bot,
                    )

        # ————————————————————————————————
        # 🩵 VNA Weekly Stats Listener
        # ————————————————————————————————
        if first_embed:
            if triggers["weekly_stats_command"] in first_embed_title:
                pretty_log(
                    "info",
                    f"Detected edit triggering VNA Weekly Stats Listener in {after.channel.name}",
                )
                await weekly_stats_listener(self.bot, before, after)
        # ————————————————————————————————
        # 🩵 VNA Monthly Stats Listener
        # ————————————————————————————————
        if first_embed:
            if triggers["monthly_stats_command"] in first_embed_title:

                pretty_log(
                    "info",
                    f"Detected edit triggering VNA Monthly Stats Listener in {after.channel.name}",
                )
                await monthly_stats_listener(self.bot, before, after)

        # ————————————————————————————————
        # 🩵 VNA Explore Caught Listener
        # ————————————————————————————————
        if content:
            if triggers["explore_listener"] in content:
                pretty_log(
                    "info",
                    f"Detected edit triggering VNA Explore Caught Listener in {after.channel.name}",
                )
                await explore_caught_listener(self.bot, before, after)

        # ————————————————————————————————
        # 🩵 VNA WB Battle Reminder Registration Confirmation
        # ————————————————————————————————
        if first_embed:
            if (
                first_embed_description
                and "<:checkedbox:752302633141665812> Successfully registered your"
                in first_embed_description
                and first_embed.title
                and "**A World Boss has spawned! Register now!**" in first_embed.title
            ):
                pretty_log(
                    "info",
                    f"Matched World Boss Battle Reminder Registration Confirmation | Message ID: {after.id} | Channel: {after.channel.name}",
                )
                await handle_wb_register_command(
                    bot=self.bot, before_message=before, message=after
                )

        # ————————————————————————————————
        # ⚡ Safari Zone Pin Alert Listener
        # ————————————————————————————————
        if first_embed:
            if first_embed_footer_text and "use a safari ball to catch it" in first_embed_footer_text.lower():
                if first_embed_author_text:
                    pin_number = get_number_after_exclamation(first_embed_author_text)
                    if pin_number:
                        await pokemon_pin_numbers_listener(
                            bot=self.bot,
                            message=after,
                            pin_number=pin_number,
                            source="safari",
                        )
        # ————————————————————————————————
        # ⚡ Missing Number Quest Timer
        # ————————————————————————————————
        if first_embed:
            if first_embed_title and "the missing numbers" in first_embed_title.lower():
                if first_embed_description and "you can submit another pin" in first_embed_description.lower():
                    pretty_log(tag="info", message=f"Missing Number Quest Timer triggered in {after.channel.name}")
                    await pin_timer_listener(
                        bot=self.bot,
                        message=after,
                    )

async def setup(bot: commands.Bot):
    await bot.add_cog(OnMessageEditCog(bot))

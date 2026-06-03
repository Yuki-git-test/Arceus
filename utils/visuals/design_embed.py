from datetime import datetime

import discord

from Constants.aesthetic import DEFAULT_EMBED_COLOR
from discord.ext import commands
from .get_pokemon_gif import get_pokemon_gif
from utils.functions.pokemon_func import get_display_name
from utils.logs.pretty_log import pretty_log

async def build_ev_tracker_embed(
    bot: commands.Bot,
    tracked_data: dict,
    evs: dict,
    goals: dict = None,
    guild: discord.Guild = None,
    user_id: int = None,
    title_prefix: str = " EV Tracker 💜",
    winner_name: str = None,
    summary_lines: list[str] = None,
    use_progress_bar: bool = False,
    max_total_evs: int = 510,
    line_separator: str = "----------------------------------------------------------",  # separator between stat lines
) -> discord.Embed:
    """
    Build a flexible EV tracker embed with spacing and line separators.
    The title prefix is now included in the author name instead of the embed title.
    """
    is_completed = False  # Track if all goals are completed
    if goals is None:
        goals = tracked_data.get("goals", {})

    stats_order = ["hp", "atk", "spa", "def", "spd", "spe"]
    total_current = sum(evs.get(s, 0) for s in stats_order)
    display_total_current = min(total_current, max_total_evs)

    # Mini progress bar helper
    def ev_bar(current, max_val=252, length=5):
        filled = int(round(length * current / max_val))
        return "💜" * filled + "▫️" * (length - filled)

    # Build 3-per-line stats with optional progress bar
    stats_lines = []
    line = []
    all_completed = True

    for i, stat in enumerate(stats_order, start=1):
        if stat in evs:
            current = evs[stat]
            goal = goals.get(stat, 252 if goals else "–")

            if current >= 252:
                completed = "✅"
            elif goal != "–" and isinstance(goal, int) and current >= goal:
                completed = "✅"
            else:
                completed = "❌" if goal != "–" else ""
                all_completed = False

            line.append(
                f"**{stat.upper()}**"
                + (f" {ev_bar(current)}" if use_progress_bar else "")
                + f" {current}/{goal} {completed}"
            )

            if i % 2 == 0:
                stats_lines.append(" |  ".join(line))
                line = []

    if line:
        stats_lines.append(" |  ".join(line))  # append remaining stats

    # Add separator between lines
    stats_str = f"\n\n".join(stats_lines)
    display_pokemon_name = get_display_name(tracked_data["pokemon"], dex=True)
    pokemon = f"{display_pokemon_name}"
    # Build description with spacing
    description = (
        f"{pokemon}\n\n"
        f"__**Total EVs:** ({display_total_current}/{max_total_evs})__\n"
        f"{stats_str}"
    )
    pokemon_name = tracked_data["pokemon"].lower()
    # gif_url = f"https://play.pokemonshowdown.com/sprites/xyani/{pokemon_name}.gif?quality=lossless"

    embed = discord.Embed(
        description=description,
        color=DEFAULT_EMBED_COLOR,
    )
    # Use shared_utils to get the gif
    gif_url = get_pokemon_gif(pokemon_name)

    if gif_url:
        embed.set_thumbnail(url=gif_url)
    else:
        pretty_log(
            tag="error",
            message=f"Cannot find Pokemon GIF for '{pokemon_name}'",
            source="GIF Embed",
        )
    # Set author with title prefix next to username
    member = guild.get_member(user_id) if guild else None
    avatar_url = member.display_avatar.url if member else None
    embed.set_author(
        name=f"{winner_name or tracked_data['user_name']}'s {title_prefix}",
        icon_url=avatar_url,
    )

    if all_completed and goals:
        embed.set_footer(
            text="🎉 All goals completed! Use /ev-tracker add to track a new Pokemon."
        )
        is_completed = True

    if summary_lines:
        embed.add_field(
            name="🔄 Updated Stats", value="\n".join(summary_lines), inline=False
        )

    return embed, is_completed


def format_bulletin_desc(*args, key_style_override: str = None) -> str:
    """
    Flexible bulletin formatter.
    - By default, keys are bold.
    - If key_style_override is provided, all keys use that style.
    - Skips any key/value pair where the value is None or empty string.
    """

    def apply_style(text: str, style: str) -> str:
        style = style.lower()
        if style == "bold":
            return f"**{text}**"
        elif style == "italic":
            return f"*{text}*"
        elif style == "underline":
            return f"__{text}__"
        elif style == "strikethrough":
            return f"~~{text}~~"
        elif style == "spoiler":
            return f"||{text}||"
        elif style == "inline_code":
            return f"`{text}`"
        elif style == "code":
            return f"```\n{text}\n```"
        elif style == "bold_upper":
            return f"**{text.upper()}**"
        else:
            return f"**{text}**"  # default bold

    key_style = key_style_override if key_style_override else "bold"

    lines = []
    i = 0
    while i < len(args):
        key = args[i]
        value = args[i + 1] if i + 1 < len(args) else None

        # 🔹 Skip if value is None or empty string
        if value is None or (isinstance(value, str) and value.strip() == ""):
            i += 2
            continue

        formatted_key = apply_style(f"{key}:", key_style)
        lines.append(f"- {formatted_key} {value}")

        i += 2

    return "\n".join(lines)


def design_embed(
    embed: discord.Embed,
    user: discord.User | discord.Member,
    thumbnail_url: str = None,
    image_url: str = None,
    footer_text: str = None,
    pokemon_name: str = None,
    color: discord.Colour | str = None,
) -> discord.Embed:
    """
    Sets the embed's author, thumbnail, image, footer, and optional color.
    - Author text = user's display name
    - Author icon = user's avatar
    - Thumbnail = thumbnail_url or user's avatar
    - Image = image_url if provided
    - Footer = footer_text or user ID
    - Color = Discord Color or Espeon shade string
    """
    avatar_url = user.display_avatar.url
    embed.set_author(name=user.display_name, icon_url=avatar_url)
    embed.timestamp = datetime.now()

    if pokemon_name:
        pokemon_gif = get_pokemon_gif(pokemon_name)
        if pokemon_gif:
            thumbnail_url = pokemon_gif

    # Set thumbnail
    embed.set_thumbnail(url=thumbnail_url or avatar_url)

    # Set image if provided
    if image_url:
        embed.set_image(url=image_url)

    # Set footer
    embed.set_footer(
        text=footer_text or f"💫 User ID: {user.id}",
        icon_url=(
            getattr(user.guild.icon, "url", None) if hasattr(user, "guild") else None
        ),
    )

    # Set color
    if isinstance(color, str):
        embed.color = DEFAULT_EMBED_COLOR
    elif isinstance(color, discord.Colour):
        embed.color = color
    else:
        embed.color = DEFAULT_EMBED_COLOR

    return embed

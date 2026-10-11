import discord

from Constants.variables import POKEMEOW_APPLICATION_ID


# 🟣────────────────────────────────────────────
#          ⚡ Get PokéMeow Reply Member ⚡
# 🟣────────────────────────────────────────────
async def get_pokemeow_reply_member(message: discord.Message) -> discord.Member | None:
    """
    Determines if the message is a PokéMeow bot reply.
    If yes, returns the member that PokéMeow replied to.
    Returns None otherwise.
    """
    # 🛑 Only process messages from PokéMeow
    if message.author.id != POKEMEOW_APPLICATION_ID:
        return None

    # 🛑 Ensure the message is a reply
    if not getattr(message, "reference", None):
        return None

    resolved_msg = getattr(message.reference, "resolved", None)
    if not isinstance(resolved_msg, discord.Message):
        return None

    member = (
        resolved_msg.author if isinstance(resolved_msg.author, discord.Member) else None
    )
    return member


def get_message_interaction_member(message: discord.Message) -> discord.Member | None:
    """
    Returns the member who triggered the interaction that created this message, if available.
    Returns None if not an interaction-created message or not a guild interaction.
    """
    interaction = getattr(message, "interaction_metadata", None)
    if interaction:
        member = getattr(interaction, "user", None)
        if isinstance(member, discord.Member):
            return member
    return None


async def get_pokemeow_reply_or_interaction_member(
    message: discord.Message,
) -> discord.Member | discord.User | None:
    """
    Returns the member who was replied to, or the interaction user as a fallback.
    """
    member = await get_pokemeow_reply_member(message)
    if member:
        return member

    return get_message_interaction_member(message)

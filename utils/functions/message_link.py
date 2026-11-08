import discord


def get_jump_to_message_link(message: discord.Message) -> str:
    guild_id = message.guild.id if message.guild else "@me"
    url = f"https://discord.com/channels/{guild_id}/{message.channel.id}/{message.id}"
    return f"[Jump to message]({url})"

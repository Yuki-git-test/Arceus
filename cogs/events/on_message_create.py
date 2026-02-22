import discord
from discord.ext import commands

from Constants.clan_wars_constants import CLAN_WARS_SERVER_ID, CLAN_WARS_TEXT_CHANNELS
from Constants.variables import (
    CC_BUMP_CHANNEL_ID,
    CC_GUILD_ID,
    POKEMEOW_APPLICATION_ID,
    PublicChannels,
    Server,
    CC_PROMO_CHANNEL_ID

)
from Constants.vn_allstars_constants import VN_ALLSTARS_TEXT_CHANNELS
from utils.clan_wars.stats_listener import stats_command_listener

# ————————————————————————————————
# 🩵 Import Listener Functions
# ————————————————————————————————
from utils.listener_func.battle_timer import battle_timer_handler
from utils.listener_func.ee_spawn_listener import (
    check_cc_bump_reminder,
    check_ee_near_spawn_alert,
    extract_boss_from_wb_command_embed,
    extract_boss_from_wb_spawn_command,
)
from utils.listener_func.faction_ball_listener import extract_faction_ball_from_fa
from utils.listener_func.fish_timer import fish_timer_handler
from utils.listener_func.incense_listener import (
    incense_command_handler,
    incense_depleted_handler,
    incense_use_handler,
    server_has_incense_handler,
)
from utils.listener_func.cc_promo_team_listener import promo_team_listener
from utils.listener_func.market_feed_listener import market_feeds_listener
from utils.listener_func.monthly_stats_listener import monthly_stats_listener
from utils.listener_func.pokemon_spawn_listener import pokemon_spawn_listener
from utils.listener_func.pokemon_timer import pokemon_timer_handler
from utils.listener_func.pokespawn_listener import as_spawn_ping
from utils.listener_func.secret_santa_listener import (
    secret_santa_listener,
    secret_santa_timer_listener,
)
from utils.listener_func.shiny_bonus_listener import (
    handle_pokemeow_global_bonus,
    read_shiny_bonus_timestamp_from_cc_channel,
)
from utils.listener_func.special_battle_npc_listener import (
    special_battle_npc_listener,
    special_battle_npc_timer_listener,
)
from utils.listener_func.wb_reg_listener import register_wb_battle_reminder
from utils.listener_func.weekly_stats_listener import weekly_stats_listener
from utils.AR.promo import promo_team
# ————————————————————————————————
# 🩵 Import DB Functions
#  ———————————————————————————————
from utils.logs.pretty_log import pretty_log

# ️────────────────────────────────────────────
#        ⚔️ Faction Names and Market Feed Channels
# ️────────────────────────────────────────────
FACTIONS = ["aqua", "flare", "galactic", "magma", "plasma", "rocket", "skull", "yell"]

MARKET_FEED_CHANNEL_IDS = {
    VN_ALLSTARS_TEXT_CHANNELS.c_u_r_s_feed,
    VN_ALLSTARS_TEXT_CHANNELS.golden_feed,
    VN_ALLSTARS_TEXT_CHANNELS.shiny_feed,
    VN_ALLSTARS_TEXT_CHANNELS.l_m_gmax_feed,
}
# ️────────────────────────────────────────────
#        ⚔️ Message Triggers
# ️────────────────────────────────────────────
triggers = {
    "wb_spawn": "spawned a world boss using 1x <:boss_coin:1249165805095092356>",
    "wb_command": "a world boss has spawned! register now!",
    "ee_vote_checker": "there is no active world boss",
    "incense_command": "Incense charges are shared & used by every player in this server",
    "has_incense": "<:incense:1202436296874922065> An `;incense` is currently active in this server!",
    "incense_depleted": "your server's incense has run out!",
    "incense_use": "Incense. Your server has received the following benefits",
    "global_bonus": "Global bonuses",
    "weekly_stats_command": "**Clan Weekly Stats — VN Allstar**",
    "monthly_stats_command": "**Clan Monthly Stats — VN Allstar**",
}
secret_santa_phrases = [
    "You sent <:PokeCoin:666879070650236928>",
    "to a random user!",
    "Your odds to receive items was boosted by",
    "You received",
]

CC_SHINY_BONUS_CHANNEL_ID = 1457171231445876746


# 🐾────────────────────────────────────────────
#        🌸 Message Create Listener Cog
# 🐾────────────────────────────────────────────
class MessageCreateListener(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # 🦋────────────────────────────────────────────
    #           👂 Message Listener Event
    # 🦋────────────────────────────────────────────
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # ————————————————————————————————
        # 🏰 Guild Check — Route by server
        # ————————————————————————————————
        guild = message.guild
        if not guild:
            return  # Skip DMs

        try:
            # ————————————————————————————————
            # 🩵 CC Bump Reminder Listener
            # ————————————————————————————————
            if guild.id == CC_GUILD_ID:
                if message.channel.id == CC_BUMP_CHANNEL_ID:
                    pretty_log(
                        "info",
                        f"Detected message in CC bump channel: Message ID {message.id}",
                        label="CC Bump Reminder Listener",
                    )
                    await check_cc_bump_reminder(self.bot, message)
                if message.channel.id == CC_SHINY_BONUS_CHANNEL_ID:
                    pretty_log(
                        "info",
                        f"Detected message in CC shiny bonus channel: Message ID {message.id}",
                        label="CC Shiny Bonus Listener",
                    )
                    await read_shiny_bonus_timestamp_from_cc_channel(
                        bot=self.bot, message=message
                    )
                if message.channel.id == CC_PROMO_CHANNEL_ID:
                    pretty_log(
                        "info",
                        f"Detected message in CC promo channel: Message ID {message.id}",
                        label="CC Promo Team Listener",
                    )
                    await promo_team_listener(bot=self.bot, message=message)
            # ————————————————————————————————
            # 🏰 Ignore non-PokéMeow bot messages
            # ————————————————————————————————
            # 🚫 Ignore all bots except PokéMeow to prevent loops
            if (
                message.author.bot
                and message.author.id != POKEMEOW_APPLICATION_ID
                and not message.webhook_id
            ):
                return

            content = message.content
            first_embed = message.embeds[0] if message.embeds else None
            first_embed_author = (
                first_embed.author.name if first_embed and first_embed.author else ""
            )
            first_embed_description = (
                first_embed.description
                if first_embed and first_embed.description
                else ""
            )
            first_embed_footer = (
                first_embed.footer.text if first_embed and first_embed.footer else ""
            )
            first_embed_title = (
                first_embed.title if first_embed and first_embed.title else ""
            )
            # ————————————————————————————————
            # 🩵 Promo Team
            # ————————————————————————————————
            if content and "!promo" in content.lower():
                pretty_log(
                    "info",
                    f"Detected !promo command message: Message ID {message.id}",
                    label="Promo Team Listener",
                )
                await promo_team(bot=self.bot, message=message)
                
            # ————————————————————————————————
            # 🩵 Clan wars server message logic
            # ————————————————————————————————
            if guild.id == CLAN_WARS_SERVER_ID:
                if first_embed:
                    if "Stats" in first_embed_author:
                        pretty_log(
                            "info",
                            f"Detected stats command embed from PokéMeow bot: Message ID {message.id}",
                            label="Clan Wars Stats Listener",
                        )
                        await stats_command_listener(
                            bot=self.bot, before_message=message, after_message=message
                        )
                if message.channel.id == CLAN_WARS_TEXT_CHANNELS.autospawn:
                    await as_spawn_ping(self.bot, message)

            # ————————————————————————————————
            # 🩵 VNA message logic
            # ————————————————————————————————
            if guild.id == Server.VNA_ID:
                first_embed = message.embeds[0] if message.embeds else None
                first_embed_description = first_embed.description if first_embed else ""
                first_embed_author = (
                    first_embed.author.name
                    if first_embed and first_embed.author
                    else ""
                )
                # ————————————————————————————————
                # 🩵 VNA Pokemon Spawn
                # ————————————————————————————————
                if content and "found a wild" in content.lower():
                    await pokemon_timer_handler(message)
                    await pokemon_spawn_listener(self.bot, message)

                # ————————————————————————————————
                # 🩵 VNA Fish Timer
                # ————————————————————————————————
                if message.embeds and message.embeds[0]:
                    embed = message.embeds[0]
                    embed_description = embed.description if embed else None
                    if (
                        embed_description
                        and "cast a" in embed_description
                        and "into the water" in embed_description
                    ):
                        await fish_timer_handler(message)
                # ————————————————————————————————
                # 🩵 VNA Battle Timer
                # ————————————————————————————————
                if first_embed_author and "PokeMeow Battles" in first_embed_author:
                    await battle_timer_handler(bot=self.bot, message=message)

                # ————————————————————————————————
                # 🩵 VNA Autospawn
                # ————————————————————————————————
                if message.channel.id == PublicChannels.Poke_Spawn:
                    await as_spawn_ping(self.bot, message)

                """# ————————————————————————————————
                # 🩵 VNA Market Snipe
                # ————————————————————————————————
                if message.channel.id in MARKET_FEED_CHANNEL_IDS:
                    await market_feeds_listener(self.bot, message)"""

                # ————————————————————————————————
                # 🩵 VNA Weekly Stats Listener
                # ————————————————————————————————
                if first_embed:
                    if triggers["weekly_stats_command"] in first_embed_title:
                        pretty_log(
                            "info",
                            f"Detected weekly stats embed from PokéMeow bot: Message ID {message.id}",
                            label="Weekly Stats Listener",
                        )
                        await weekly_stats_listener(
                            bot=self.bot, before_message=message, after_message=message
                        )
                # ————————————————————————————————
                # 🩵 VNA Monthly Stats Listener
                # ————————————————————————————————
                if first_embed:
                    if triggers["monthly_stats_command"] in first_embed_title:
                        pretty_log(
                            "info",
                            f"Detected monthly stats embed from PokéMeow bot: Message ID {message.id}",
                            label="Monthly Stats Listener",
                        )
                        await monthly_stats_listener(
                            bot=self.bot, before_message=message, after_message=message
                        )
                # 🔧───────────────────────────────────────────────🔧
                # 🔧    🩵 World Boss Spawn Listener
                # 🔧───────────────────────────────────────────────🔧
                if message.content:
                    if triggers["wb_spawn"] in message.content.lower():
                        pretty_log(
                            "info",
                            f"Detected world boss spawn message from PokéMeow bot: Message ID {message.id}",
                            label="World Boss Spawn Listener",
                        )
                        await extract_boss_from_wb_spawn_command(
                            bot=self.bot, message=message
                        )

                # 🔧───────────────────────────────────────────────🔧
                # 🔧    🩵 World Boss Command Embed Listener
                # 🔧───────────────────────────────────────────────🔧
                if message.embeds:
                    embed_title = (
                        message.embeds[0].title if message.embeds[0].title else ""
                    )
                    if triggers["wb_command"] in embed_title.lower():
                        pretty_log(
                            "info",
                            f"Detected world boss command embed from PokéMeow bot: Message ID {message.id}",
                            label="World Boss Command Embed Listener",
                        )
                        await extract_boss_from_wb_command_embed(
                            bot=self.bot, message=message
                        )

                # 🔧───────────────────────────────────────────────🔧
                # 🔧    🩵 EE Near Spawn Alert Checker
                # 🔧───────────────────────────────────────────────🔧
                if message.embeds:
                    embed_title = (
                        message.embeds[0].title if message.embeds[0].title else ""
                    )
                    if triggers["ee_vote_checker"] in embed_title.lower():
                        pretty_log(
                            "info",
                            f"Detected EE vote checker embed from PokéMeow bot: Message ID {message.id}",
                            label="EE Near Spawn Alert Checker",
                        )
                        await check_ee_near_spawn_alert(bot=self.bot, message=message)

                # 🔧───────────────────────────────────────────────🔧
                # 🔧 🩵 Faction Ball Listener from ;fa
                # 🔧───────────────────────────────────────────────🔧
                if first_embed:
                    if first_embed.author and any(
                        f in first_embed.author.name.lower() for f in FACTIONS
                    ):
                        await extract_faction_ball_from_fa(
                            bot=self.bot, message=message
                        )
                # 🔧───────────────────────────────────────────────🔧
                # 🔧    🩵 WB Battle Reminder Registration Listener
                # 🔧───────────────────────────────────────────────🔧
                if first_embed:
                    if first_embed_description:
                        if (
                            "<:checkedbox:752302633141665812> You are registered for this fight"
                            in first_embed_description
                            and ";wb fight" in first_embed_description
                        ):
                            await register_wb_battle_reminder(
                                bot=self.bot, message=message
                            )
                # ————————————————————————————————
                # 🩵 Special Battle NPC Listeners
                # ————————————————————————————————
                if first_embed:
                    if (
                        first_embed.description
                        and "challenged <:xmas_blue:1451059140955734110> **XMAS Blue** to a battle!"
                        in first_embed.description
                    ):
                        pretty_log(
                            "info",
                            f"🔹 Matched Special Battle NPC Listener for XMAS BLUE | message_id={message.id}",
                        )
                        await special_battle_npc_listener(bot=self.bot, message=message)
                if (
                    content
                    and ":x: You cannot fight XMAS Blue yet! He will be available for you to re-battle"
                    in content
                ):
                    pretty_log(
                        "info",
                        f"🔹 Matched Special Battle NPC Timer Listener for XMAS BLUE | message_id={message.id}",
                    )
                    await special_battle_npc_timer_listener(
                        bot=self.bot, message=message
                    )
                # ————————————————————————————————
                # 🩵 Secret Santa Listeners
                # ————————————————————————————————
                if message.content:
                    # Check if all ss phrases are in the message content
                    if all(
                        phrase in message.content for phrase in secret_santa_phrases
                    ):
                        pretty_log(
                            "info",
                            f"🎅 Matched Secret Santa Listener | Message ID: {message.id} | Channel: {message.channel.name}",
                        )
                        await secret_santa_listener(bot=self.bot, message=message)
                # Secret Santa Timer Listener
                if message.content:
                    if ":x: You may send out another gift on" in message.content:
                        pretty_log(
                            "info",
                            f"🎅 Matched Secret Santa Timer Listener | Message ID: {message.id} | Channel: {message.channel.name}",
                        )
                        await secret_santa_timer_listener(bot=self.bot, message=message)
            # ————————————————————————————————
            # 🩵 Shiny Bonus Listener
            # ————————————————————————————————
            if first_embed:
                if triggers["global_bonus"] in first_embed_title:
                    pretty_log(
                        "info",
                        f"Detected global bonus embed from PokéMeow bot: Message ID {message.id}",
                        label="Shiny Bonus Listener",
                    )
                    await handle_pokemeow_global_bonus(bot=self.bot, message=message)
            # ————————————————————————————————
            # 🩵 Incense Listeners
            # ————————————————————————————————
            if first_embed:
                # Incense Command Handler
                if triggers["incense_command"] in first_embed_footer:
                    pretty_log(
                        "info",
                        f"Detected incense command embed from PokéMeow bot: Message ID {message.id}",
                        label="Incense Command Handler",
                    )
                    await incense_command_handler(bot=self.bot, message=message)
            if message.content and triggers["incense_use"] in message.content:
                pretty_log(
                    "info",
                    f"Detected incense use message from PokéMeow bot: Message ID {message.id}",
                    label="Incense Use Handler",
                )
                await incense_use_handler(bot=self.bot, message=message)

            if message.content and triggers["has_incense"] in message.content:
                await server_has_incense_handler(bot=self.bot, message=message)

            if message.content and triggers["incense_depleted"] in message.content:
                pretty_log(
                    "info",
                    f"Detected incense depleted message from PokéMeow bot: Message ID {message.id}",
                    label="Incense Depleted Handler",
                )
                await incense_depleted_handler(bot=self.bot, message=message)

        except Exception as e:
            # 🛑────────────────────────────────────────────
            #        Unhandled on_message Error Handler
            # 🛑────────────────────────────────────────────
            pretty_log(
                "critical",
                f"Unhandled exception in on_message: {e}",
                label="MESSAGE",
                bot=self.bot,
                include_trace=True,
            )


# 🌈────────────────────────────────────────────
#        🛠️ Setup function to add cog to bot
# 🌈────────────────────────────────────────────
async def setup(bot: commands.Bot):
    await bot.add_cog(MessageCreateListener(bot))

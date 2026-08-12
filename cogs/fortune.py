import discord
from discord.ext import commands
import random
import asyncio
import pytz
from datetime import datetime

OWNER_ID = 705447976658665552  # Replace with your Discord user ID

class Fortune(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.used_fortunes = {}  # user_id: datetime.date

        self.fortunes = {
            5: {
                "name": "Daikichi",
                "kanji": "大吉",
                "meaning": "Great Blessing",
                "messages": [
                    "A wave of good fortune surrounds you. Prosper in all you do.",
                    "The heavens bless your path—everything shall flow your way.",
                    "Joy, success, and love shine brightly ahead.",
                    "This year, nothing can stand in your way. Embrace it.",
                    "Good fortune rains like cherry blossoms in the spring."
                ]
            },
            4: {
                "name": "Chūkichi",
                "kanji": "中吉",
                "meaning": "Moderate Blessing",
                "messages": [
                    "A favorable breeze blows, but steer wisely.",
                    "Fortune follows effort—keep pushing forward.",
                    "Opportunities bloom, though weeds remain. Tread carefully.",
                    "Some clouds may linger, but the sky is clearing.",
                    "Good things arrive steadily, not all at once."
                ]
            },
            3: {
                "name": "Shōkichi",
                "kanji": "小吉",
                "meaning": "Small Blessing",
                "messages": [
                    "A small joy brightens your day. Cherish it.",
                    "Not all luck is grand, but even drops fill a cup.",
                    "A fleeting spark of fortune dances near you.",
                    "Small gains lead to bigger blessings.",
                    "Tiny treasures await in quiet corners."
                ]
            },
            2: {
                "name": "Suekichi",
                "kanji": "末吉",
                "meaning": "Future Blessing",
                "messages": [
                    "Patience will reveal the blessings meant for you.",
                    "The bud has not yet bloomed. Be gentle and wait.",
                    "Winds of fortune gather slowly. Stand firm.",
                    "Keep planting seeds. Growth comes with time.",
                    "Good fortune sleeps—wake it with persistence."
                ]
            },
            1: {
                "name": "Kyō",
                "kanji": "凶",
                "meaning": "Curse",
                "messages": [
                    "Caution is your best ally this season.",
                    "A misstep may come—walk slowly and wisely.",
                    "Troubled waters ahead. Find safe shorelines.",
                    "Silence and stillness are your shield.",
                    "Luck fades for now—light your own path."
                ]
            },
            0: {
                "name": "Daikyō",
                "kanji": "大凶",
                "meaning": "Great Curse",
                "messages": [
                    "Dark winds stir. Stay vigilant and delay risky plans.",
                    "Disaster lurks in haste. Retreat and reflect.",
                    "When shadows fall, light must come from within.",
                    "Even stars dim. Be still until dawn returns.",
                    "Troubles gather—tie your hopes to tomorrow."
                ]
            }
        }

        self.repeat_messages = [
            "🌸 You've already drawn your fortune today. Let fate rest until tomorrow~",
            "🧧 Only one fortune per day! The shrine maiden’s asleep now~",
            "⛩️ Patience, seeker. A new fortune awaits at midnight!",
            "📜 Your destiny has already been revealed today, wanderer.",
            "🎐 Come back tomorrow—new winds bring new omens."
        ]

    @commands.command()
    async def fortune(self, ctx):
        user_id = ctx.author.id

        # Timezone-aware date check (EST)
        now = datetime.now(pytz.timezone("America/New_York"))
        today = now.date()

        # Admin bypass
        if user_id != OWNER_ID:
            last_draw = self.used_fortunes.get(user_id)
            if last_draw == today:
                return await ctx.send(random.choice(self.repeat_messages))

        # Step 1: Send gif
        file = discord.File("PICS/fortune.gif", filename="fortune.gif")
        embed = discord.Embed()
        embed.set_image(url="attachment://fortune.gif")
        message = await ctx.send(file=file, embed=embed)

        # Step 2: Wait
        await asyncio.sleep(1.5)

        # Step 3: Generate stats
        money = random.randint(1, 5)
        love = random.randint(1, 5)
        luck = random.randint(1, 5)
        overall = max(0, min(5, round((money + love + luck) / 3)))

        fortune_data = self.fortunes.get(overall)
        if not fortune_data:
            return await message.edit(content="⚠️ An error occurred while drawing your fortune.")

        name = fortune_data["name"]
        kanji = fortune_data["kanji"]
        meaning = fortune_data["meaning"]
        message_text = random.choice(fortune_data["messages"])

        def stars(n): return "★" * n + "☆" * (5 - n)
        sakura = "🌸" * luck

        new_embed = discord.Embed(description=(
            f"🔮 You shake the fortune box and draw a stick...\n\n"
            f"🧧 Your Fortune: **{name} – {kanji} ({meaning})**\n*{message_text}*\n\n"
            f"💰 金運 (money)：{stars(money)}\n"
            f"💖 恋愛運 (love)：{stars(love)}\n"
            f"🍀 総合運 (luck)：{sakura}\n"
            f"**Overall:** {stars(overall)}"
        ))

        await message.edit(content=None, attachments=[], embed=new_embed)

        if user_id != OWNER_ID:
            self.used_fortunes[user_id] = today

    fortune.extras = {"category": "Public"}

# Extension loader
async def setup(bot):
    await bot.add_cog(Fortune(bot))

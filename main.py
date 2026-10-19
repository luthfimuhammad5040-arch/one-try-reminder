import os
import discord
from discord.ext import tasks
from datetime import time
from zoneinfo import ZoneInfo

TOKEN = os.environ["DISCORD_TOKEN"]
CHANNEL_ID = int(os.environ["CHANNEL_ID"])

REMINDER_MESSAGE = os.getenv(
    "REMINDER_MESSAGE",
    "Reminder untuk seluruh member ONE TRY COMMUNITY!\n"
    "Jangan lupa mampir dan ramaikan server kita. "
    "Tetap aktif, jaga kekompakan, dan pantau informasi terbaru!"
)

TIMEZONE = ZoneInfo("Asia/Jakarta")

intents = discord.Intents.default()
client = discord.Client(intents=intents)


@tasks.loop(
    time=time(hour=9, minute=0, tzinfo=TIMEZONE)
)
async def daily_reminder():
    try:
        channel = client.get_channel(CHANNEL_ID)

        if channel is None:
            channel = await client.fetch_channel(CHANNEL_ID)

        embed = discord.Embed(
            title="ONE TRY COMMUNITY | DAILY REMINDER",
            description=REMINDER_MESSAGE,
            color=discord.Color.blue()
        )
        embed.set_footer(
            text="ONE TRY COMMUNITY • Daily Reminder"
        )

        await channel.send(
            content="@everyone",
            embed=embed,
            allowed_mentions=discord.AllowedMentions(
                everyone=True,
                users=False,
                roles=False
            )
        )

        print("Reminder harian berhasil dikirim.")

    except Exception as error:
        print(f"Gagal mengirim reminder: {error}")


@daily_reminder.before_loop
async def before_reminder():
    await client.wait_until_ready()


@client.event
async def on_ready():
    print(f"Bot aktif: {client.user}")

    if not daily_reminder.is_running():
        daily_reminder.start()


client.run(TOKEN)

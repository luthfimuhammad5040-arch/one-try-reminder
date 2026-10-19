
import os
import discord
from discord.ext import tasks
from datetime import time
from zoneinfo import ZoneInfo

TOKEN = os.environ["DISCORD_TOKEN"]
CHANNEL_ID = int(os.environ["CHANNEL_ID"])
TIMEZONE = ZoneInfo("Asia/Jakarta")

REMINDER_MESSAGE = os.getenv(
    "REMINDER_MESSAGE",
    "Mohon berhati-hati terhadap penipuan Robux. "
    "Staff resmi tidak pernah meminta password atau kode verifikasi."
)

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = discord.app_commands.CommandTree(client)


async def send_reminder():
    channel = client.get_channel(CHANNEL_ID)

    if channel is None:
        channel = await client.fetch_channel(CHANNEL_ID)

    embed = discord.Embed(
        title="REMINDER MEMBER ONE TRY COMMUNITY",
        description=REMINDER_MESSAGE,
        color=discord.Color.blue()
    )
    embed.set_footer(text="ONE TRY COMMUNITY")

    await channel.send(
        content="@everyone",
        embed=embed,
        allowed_mentions=discord.AllowedMentions(
            everyone=True,
            users=False,
            roles=False
        )
    )


@tree.command(
    name="tesreminder",
    description="Tes pengiriman reminder ONE TRY COMMUNITY"
)
async def tesreminder(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message(
            "Hanya administrator yang dapat menjalankan perintah ini.",
            ephemeral=True
        )
        return

    await interaction.response.defer(ephemeral=True)

    try:
        await send_reminder()
        await interaction.followup.send(
            "Reminder berhasil dikirim ke channel tujuan.",
            ephemeral=True
        )
    except Exception as error:
        print(f"Tes reminder gagal: {error}")
        await interaction.followup.send(
            "Gagal mengirim reminder. Periksa izin bot dan Railway Logs.",
            ephemeral=True
        )


@tasks.loop(time=time(hour=9, minute=0, tzinfo=TIMEZONE))
async def daily_reminder():
    try:
        await send_reminder()
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


async def setup_commands():
    await tree.sync()
    print("Perintah slash berhasil disinkronkan.")


@client.event
async def setup_hook():
    await setup_commands()


client.run(TOKEN)

import os
import asyncio
import discord
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

TOKEN = os.environ["DISCORD_TOKEN"]
CHANNEL_ID = int(os.environ["CHANNEL_ID"])
TIMEZONE = ZoneInfo("Asia/Jakarta")

# PENGATURAN REMINDER
INTERVAL_HARI = 2
JAM_REMINDER = 9
MENIT_REMINDER = 0

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


# PERINTAH TES REMINDER
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


# MENENTUKAN JADWAL PERTAMA
def hitung_jadwal_berikutnya():
    sekarang = datetime.now(TIMEZONE)

    jadwal = sekarang.replace(
        hour=JAM_REMINDER,
        minute=MENIT_REMINDER,
        second=0,
        microsecond=0
    )

    if sekarang >= jadwal:
        jadwal += timedelta(days=1)

    return jadwal


# REMINDER OTOMATIS SETIAP 2 HARI
async def reminder_scheduler():
    await client.wait_until_ready()

    jadwal_berikutnya = hitung_jadwal_berikutnya()

    print(
        "Jadwal reminder berikutnya:",
        jadwal_berikutnya.strftime("%d-%m-%Y %H:%M WIB")
    )

    while not client.is_closed():

        sekarang = datetime.now(TIMEZONE)

        if sekarang >= jadwal_berikutnya:
            try:
                await send_reminder()

                print(
                    "Reminder berhasil dikirim:",
                    datetime.now(TIMEZONE).strftime("%d-%m-%Y %H:%M WIB")
                )

                jadwal_berikutnya += timedelta(
                    days=INTERVAL_HARI
                )

                print(
                    "Jadwal reminder selanjutnya:",
                    jadwal_berikutnya.strftime("%d-%m-%Y %H:%M WIB")
                )

            except Exception as error:
                print(f"Gagal mengirim reminder: {error}")

                # Coba lagi setelah 10 menit jika gagal.
                jadwal_berikutnya = (
                    datetime.now(TIMEZONE) + timedelta(minutes=10)
                )

        waktu_tunggu = max(
            1,
            (jadwal_berikutnya - datetime.now(TIMEZONE)).total_seconds()
        )

        await asyncio.sleep(min(waktu_tunggu, 60))


# SAAT BOT ONLINE
@client.event
async def on_ready():
    print(f"Bot aktif: {client.user}")

    if not hasattr(client, "reminder_task"):
        client.reminder_task = asyncio.create_task(
            reminder_scheduler()
        )


# SINKRONISASI SLASH COMMAND
async def setup_hook():
    await tree.sync()
    print("Perintah slash berhasil disinkronkan.")


client.setup_hook = setup_hook

client.run(TOKEN)


from slash_commands import setup_slash_commands
from disney_checker import check_reservations_periodically
from discord.ext import commands
import discord
import os

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"🤖 Logged in as {bot.user}")
    await setup_slash_commands(bot)
    check_reservations_periodically.start(bot)

print(f"DISCORD_BOT_TOKEN present? {'Yes' if os.getenv('DISCORD_BOT_TOKEN') else 'No'}")

bot.run(os.getenv("DISCORD_BOT_TOKEN"))

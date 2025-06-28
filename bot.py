from dotenv import load_dotenv
load_dotenv()

import discord
from discord.ext import commands
import os
from slash_commands import setup_slash_commands
from disney_checker import check_reservations_periodically
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"🤖 Logged in as {bot.user}")
    await setup_slash_commands(bot)
    check_reservations_periodically.start(bot)

if __name__ == "__main__":
    token = os.getenv("DISCORD_BOT_TOKEN")
    if not token:
        print("❌ DISCORD_BOT_TOKEN not found!")
    else:
        bot.run(token)


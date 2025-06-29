import os
from dotenv import load_dotenv

# Load environment variables (DISCORD_BOT_TOKEN, etc.)
load_dotenv()

import discord
from discord.ext import commands
from slash_commands import setup_slash_commands
from disney_checker import check_reservations_periodically

intents = discord.Intents.default()
intents.messages = True  # We need to read user messages for the slash command flow
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"🤖 Logged in as {bot.user}")
    # Set up slash commands and background tasks
    await setup_slash_commands(bot)
    # Start the periodic reservation checking loop (runs every 5 minutes)
    check_reservations_periodically.start(bot)

if __name__ == "__main__":
    token = os.getenv("DISCORD_BOT_TOKEN")
    if not token:
        print("❌ DISCORD_BOT_TOKEN not found! Please set it in the environment.")
    else:
        bot.run(token)

import discord
from discord.ext import commands
from slash_commands import setup_slash_commands
import os

intents = discord.Intents.default()
intents.message_content = False

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"🤖 Logged in as {bot.user}")
    print("🌐 Initial restaurant list loading...")
    await setup_slash_commands(bot)

if __name__ == "__main__":
    token = os.getenv("DISCORD_BOT_TOKEN")
    if not token:
        raise Exception("DISCORD_BOT_TOKEN not found in environment variables.")
    bot.run(token)

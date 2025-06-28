import discord
from discord.ext import commands, tasks
from restaurants_scraper import scrape_and_save_restaurants
from slash_commands import register_slash_commands
from disney_checker import check_reservations_periodically
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")

intents = discord.Intents.default()
client = commands.Bot(command_prefix="!", intents=intents)

@client.event
async def on_ready():
    print(f"🤖 Logged in as {client.user}")
    scrape_and_save_restaurants()
    await register_slash_commands(client)
    check_reservations_periodically.start(client)

client.run(TOKEN)

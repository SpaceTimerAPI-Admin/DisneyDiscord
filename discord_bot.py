import discord
import json
import os
from discord.ext import commands
from dotenv import load_dotenv
from rapidfuzz import process

load_dotenv()
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

RESTAURANTS = ["Ohana", "Be Our Guest", "Chef Mickey's", "California Grill", "Cinderella's Royal Table"]

def load_requests():
    try:
        with open("user_requests.json", "r") as f:
            return json.load(f)
    except:
        return {}

def save_requests(data):
    with open("user_requests.json", "w") as f:
        json.dump(data, f, indent=2)

@bot.event
async def on_ready():
    print(f'✅ Logged in as {bot.user}')

@bot.command(name='alert')
async def alert(ctx, restaurant: str, date: str, time: str):
    user_id = str(ctx.author.id)
    rest_match, score, _ = process.extractOne(restaurant, RESTAURANTS)

    if score < 70:
        await ctx.send(f"❓ Did you mean **{rest_match}**? Please try again.")
        return

    data = load_requests()
    data.setdefault(user_id, []).append({
        "restaurant": rest_match,
        "date": date,
        "time_range": [time, time]
    })
    save_requests(data)

    await ctx.send(f"✅ Got it! You’ll get a DM if **{rest_match}** opens on {date} at {time}.")

bot.run(os.getenv("DISCORD_BOT_TOKEN"))

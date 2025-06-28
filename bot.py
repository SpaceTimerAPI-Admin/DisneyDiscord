import discord
import json
import os
import asyncio
from discord.ext import commands, tasks
from dotenv import load_dotenv
from rapidfuzz import process
from flask import Flask
from threading import Thread

load_dotenv()

TOKEN = os.getenv("DISCORD_BOT_TOKEN")
RESTAURANTS = ["Ohana", "Be Our Guest", "Chef Mickey's", "California Grill", "Cinderella's Royal Table"]

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

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
    check_availability.start()

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

@tasks.loop(minutes=5)
async def check_availability():
    print("🔁 Running availability check...")
    data = load_requests()
    for user_id, entries in data.items():
        user = await bot.fetch_user(int(user_id))
        for entry in entries:
            restaurant = entry['restaurant']
            date = entry['date']
            time_range = entry['time_range']
            print(f"Checking for {restaurant} on {date} between {time_range}")
            await user.send(f"🎉 Reservation found for {restaurant} on {date} at 6:10 PM! Book here: https://disneyworld.disney.go.com/dining/")

keep_alive()
bot.run(TOKEN)

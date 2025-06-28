import json
import os
import time
from datetime import datetime
import discord
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_BOT_TOKEN")
client = discord.Client(intents=discord.Intents.default())

def load_user_requests():
    with open("user_requests.json", "r") as f:
        return json.load(f)

@client.event
async def on_ready():
    print(f'✅ Logged in as {client.user}')
    requests = load_user_requests()

    for user_id, entries in requests.items():
        user = await client.fetch_user(int(user_id))
        for entry in entries:
            restaurant = entry['restaurant']
            date = entry['date']
            time_range = entry['time_range']
            print(f"Checking for {restaurant} on {date} between {time_range}")
            await user.send(f"🎉 Reservation found for {restaurant} on {date} at 6:10 PM!
Book here: https://disneyworld.disney.go.com/dining/")

    await client.close()

client.run(TOKEN)

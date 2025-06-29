import discord
from discord import app_commands
from discord.ext import tasks
import asyncio
from rapidfuzz import process
from restaurant_scraper import get_all_restaurants

latest_restaurants = []
user_requests = {}  # Track where each user is in the flow

@tasks.loop(minutes=60)
async def refresh_restaurants():
    global latest_restaurants
    print("🔄 Refreshing restaurant list...")
    latest_restaurants = get_all_restaurants()
    print(f"✅ Loaded {len(latest_restaurants)} restaurants.")

async def setup_slash_commands(bot: discord.Client):
    tree = bot.tree

    @tree.command(name="request", description="Request a Disney Dining Alert")
    async def request(interaction: discord.Interaction):
        await interaction.response.send_message("🍽️ What restaurant are you looking for?", ephemeral=True)
        user_requests[interaction.user.id] = {"step": "restaurant"}

    await tree.sync()

    if not refresh_restaurants.is_running():
        refresh_restaurants.start()

    @bot.event
    async def on_message(message: discord.Message):
        if message.author.bot:
            return

        state = user_requests.get(message.author.id)
        if not state:
            return

        # Step 1: Match restaurant name
        if state["step"] == "restaurant":
            query = message.content.strip()
            match_result = process.extractOne(query, latest_restaurants)
            if match_result:
                match, score, _ = match_result
                if score > 80:
                    state.update({"step": "date", "restaurant": match})
                    await message.channel.send(f"✅ Matched: **{match}**. What date? (MM/DD/YYYY)")
                else:
                    await message.channel.send("❌ No close match found. Try again with `/request`.")
                    user_requests.pop(message.author.id, None)
            else:
                await message.channel.send("❌ No match found. Try again with `/request`.")
                user_requests.pop(message.author.id, None)

        # Step 2: Get the date
        elif state["step"] == "date":
            date = message.content.strip()
            state.update({"step": "time", "date": date})
            await message.channel.send("⏰ What time are you hoping for? (e.g., 6:30 PM)")

        # Step 3: Get the time
        elif state["step"] == "time":
            time = message.content.strip()
            restaurant = state["restaurant"]
            date = state["date"]
            await message.channel.send(
                f"✅ All set! We’ll track **{restaurant}** on **{date}** at **{time}** for availability alerts. 🎉"
            )
            # TODO: Save alert to database or start monitoring here
            user_requests.pop(message.author.id, None)

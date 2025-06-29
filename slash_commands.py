
import discord
from discord import app_commands
from discord.ext import tasks
import asyncio
from rapidfuzz import process
from restaurant_scraper import get_all_restaurants

latest_restaurants = []

@tasks.loop(minutes=60)
async def refresh_restaurants():
    global latest_restaurants
    print("🔄 Refreshing restaurant list...", flush=True)
    try:
        latest_restaurants = get_all_restaurants()
        print(f"✅ Loaded {len(latest_restaurants)} restaurants.", flush=True)
    except Exception as e:
        print(f"❌ Failed to refresh restaurants: {e}", flush=True)

async def setup_slash_commands(bot: discord.Client):
    tree = bot.tree

    @tree.command(name="request", description="Request a Disney Dining Alert")
    async def request(interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        if not latest_restaurants:
            await interaction.followup.send("⚠️ Restaurant list is still loading. Please try again shortly.")
            return

        await interaction.followup.send("🍽️ What restaurant are you looking for?")

        def check(msg):
            return msg.author.id == interaction.user.id and msg.channel == interaction.channel

        try:
            msg = await bot.wait_for("message", check=check, timeout=60)
            query = msg.content.strip()
            result = process.extractOne(query, latest_restaurants)
            if result is None:
                await interaction.followup.send("❌ Couldn't find a match. Try again with `/request`.")
                return

            match, score, _ = result
            if score > 80:
                await interaction.followup.send(f"✅ Matched: **{match}**. What date? (MM/DD/YYYY)")
            else:
                await interaction.followup.send("❌ No close match. Try again with `/request`.")
        except asyncio.TimeoutError:
            await interaction.followup.send("⏰ Timeout. Start again with `/request`.")

    await tree.sync()

    if not refresh_restaurants.is_running():
        refresh_restaurants.start()

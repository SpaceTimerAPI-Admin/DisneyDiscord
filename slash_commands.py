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
    print("🔄 Refreshing restaurant list...")
    latest_restaurants = get_all_restaurants()  # ✅ No await needed
    print(f"✅ Loaded {len(latest_restaurants)} restaurants.")

async def setup_slash_commands(bot: discord.Client):
    tree = bot.tree  # ✅ Use the bot's existing CommandTree

    @tree.command(name="request", description="Request a Disney Dining Alert")
    async def request(interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send("🍽️ What restaurant are you looking for?")

        def check(msg):
            return msg.author.id == interaction.user.id and msg.channel == interaction.channel

        try:
            msg = await bot.wait_for("message", check=check, timeout=60)
            query = msg.content.strip()
            match, score, _ = process.extractOne(query, latest_restaurants)
            if score > 80:
                await interaction.followup.send(f"✅ Matched: **{match}**. What date? (MM/DD/YYYY)")
            else:
                await interaction.followup.send("❌ No close match. Try again with `/request`.")
        except asyncio.TimeoutError:
            await interaction.followup.send("⏰ Timeout. Start again with `/request`.")

    await tree.sync()

    if not refresh_restaurants.is_running():
        refresh_restaurants.start()

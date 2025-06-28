import discord
from discord import app_commands
from rapidfuzz import process
import asyncio
from restaurant_scraper import get_all_restaurants

ALL_RESTAURANTS = []

async def setup_slash_commands(bot):
    tree = bot.tree

    @tree.command(name="request", description="Request a Disney Dining Alert")
async def request(interaction: discord.Interaction):
    await interaction.response.defer(thinking=True, ephemeral=True)  # ✅ DEFER IMMEDIATELY

    await interaction.followup.send("🍽️ What restaurant are you looking for?")

    def check(msg):
        return msg.author.id == interaction.user.id and msg.channel == interaction.channel

    try:
        msg = await bot.wait_for("message", check=check, timeout=60)
        restaurant_name = msg.content.strip()

        # Make sure the restaurant scraper has been run recently or run here if needed
        from restaurant_scraper import get_restaurant_names
        all_restaurants = get_restaurant_names()

        match, score, _ = process.extractOne(restaurant_name, all_restaurants)
        if score > 80:
            await interaction.followup.send(f"✅ Matched restaurant: **{match}**. What date are you looking for? (MM/DD/YYYY)")
        else:
            await interaction.followup.send("❌ Couldn't find a close restaurant match. Try again using `/request`.")
    except asyncio.TimeoutError:
        await interaction.followup.send("⏰ Timeout! Please start again using `/request`.")

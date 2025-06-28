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
        global ALL_RESTAURANTS
        ALL_RESTAURANTS = get_all_restaurants()

        await interaction.response.send_message("🍽️ What restaurant are you looking for?", ephemeral=True)

        def check(msg):
            return msg.author.id == interaction.user.id and msg.channel == interaction.channel

        try:
            msg = await bot.wait_for("message", check=check, timeout=60)
            restaurant_name = msg.content.strip()

            match, score, _ = process.extractOne(restaurant_name, ALL_RESTAURANTS)
            if score > 80:
                await interaction.followup.send(f"✅ Matched restaurant: **{match}**. What date are you looking for? (MM/DD/YYYY)")
            else:
                await interaction.followup.send("❌ Couldn't find a close restaurant match. Try again using `/request`.", ephemeral=True)
        except asyncio.TimeoutError:
            await interaction.followup.send("⏰ Timeout! Please start again using `/request`.", ephemeral=True)

    await tree.sync()
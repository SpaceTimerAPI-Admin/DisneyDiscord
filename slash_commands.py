import discord
from discord import app_commands
from rapidfuzz import process
from discord.ext import tasks
import asyncio
import json
import os
from restaurant_scraper import get_all_restaurants

ALL_RESTAURANTS = []

async def setup_slash_commands(bot):
    tree = bot.tree

    @tree.command(name="request", description="Request a Disney Dining Alert")
    async def request(interaction: discord.Interaction):
        await interaction.response.defer(thinking=True, ephemeral=True)

        await interaction.followup.send("\U0001F37D\uFE0F What restaurant are you looking for?")

        def check(msg):
            return msg.author.id == interaction.user.id and msg.channel == interaction.channel

        try:
            msg = await bot.wait_for("message", check=check, timeout=60)
            restaurant_name = msg.content.strip()

            match, score, _ = process.extractOne(restaurant_name, ALL_RESTAURANTS)
            if score > 80:
                await interaction.followup.send(f"\u2705 Matched restaurant: **{match}**. What date are you looking for? (MM/DD/YYYY)")
            else:
                await interaction.followup.send("\u274C Couldn't find a close restaurant match. Try again using `/request`.", ephemeral=True)
        except asyncio.TimeoutError:
            await interaction.followup.send("\u23F0 Timeout! Please start again using `/request`.", ephemeral=True)

    await tree.sync()

@tasks.loop(hours=1)
async def refresh_restaurants():
    global ALL_RESTAURANTS
    ALL_RESTAURANTS = scrape_restaurants()
    with open("restaurants.json", "w") as f:
        json.dump(ALL_RESTAURANTS, f, indent=2)

refresh_restaurants.start()

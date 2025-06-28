import discord
from discord import app_commands
from rapidfuzz import process
from discord.ext import tasks
import asyncio
import json

with open("restaurants.json", "r") as f:
    ALL_RESTAURANTS = json.load(f)

async def setup_slash_commands(bot):
    @bot.tree.command(name="request", description="Request a Disney Dining Alert")
    async def request(interaction: discord.Interaction):
        # Immediately acknowledge the interaction to avoid "outdated" message
        await interaction.response.send_message("🍽️ What restaurant are you looking for?", ephemeral=True)

        def check(msg):
            return msg.author.id == interaction.user.id and msg.channel == interaction.channel

        try:
            msg = await bot.wait_for("message", check=check, timeout=60)
            restaurant_name = msg.content.strip()

            match, score, _ = process.extractOne(restaurant_name, ALL_RESTAURANTS)
            if score > 80:
                await interaction.followup.send(
                    f"✅ Matched restaurant: **{match}**. What date are you looking for? (MM/DD/YYYY)",
                    ephemeral=True
                )
            else:
                await interaction.followup.send(
                    "❌ Couldn't find a close restaurant match. Try again using `/request`.",
                    ephemeral=True
                )
        except asyncio.TimeoutError:
            await interaction.followup.send("⏰ Timeout! Please start again using `/request`.", ephemeral=True)

    await bot.tree.sync()

import discord
from discord import app_commands
from rapidfuzz import process
import json
import os

with open("restaurants.json", "r") as f:
    ALL_RESTAURANTS = json.load(f)

class RequestView(discord.ui.View):
    def __init__(self, user, interaction, original_input, match, all_matches):
        super().__init__(timeout=60)
        self.user = user
        self.interaction = interaction
        self.original_input = original_input
        self.match = match
        self.all_matches = all_matches

    @discord.ui.button(label="Yes", style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(f"✅ Great! We'll move forward with **{self.match}**. Please reply with your date (YYYY-MM-DD).", ephemeral=True)
        # Save temp user state if needed

    @discord.ui.button(label="No", style=discord.ButtonStyle.red)
    async def deny(self, interaction: discord.Interaction, button: discord.ui.Button):
        suggestions = ', '.join(self.all_matches)
        await interaction.response.send_message(f"❌ No problem. Try a new restaurant name. Suggestions: {suggestions}", ephemeral=True)

async def setup_slash_commands(bot):
    @bot.tree.command(name="request", description="Request a Disney dining reservation alert")
    async def request(interaction: discord.Interaction):
        await interaction.response.send_message("🍽️ What restaurant are you looking for?", ephemeral=True)

        def check(m):
            return m.author.id == interaction.user.id and m.channel == interaction.channel

        try:
            msg = await bot.wait_for("message", timeout=60.0, check=check)
            user_input = msg.content.strip()

            matches = process.extract(user_input, ALL_RESTAURANTS.keys(), limit=3, score_cutoff=60)
            if matches:
                best_match = matches[0][0]
                suggestion_view = RequestView(interaction.user, interaction, user_input, best_match, [m[0] for m in matches])
                await interaction.followup.send(f"Did you mean **{best_match}**?", view=suggestion_view, ephemeral=True)
            else:
                await interaction.followup.send("❌ No close matches found. Please try again with a different name.", ephemeral=True)

        except Exception as e:
            await interaction.followup.send("⏱️ Timed out. Please use /request again to restart.", ephemeral=True)

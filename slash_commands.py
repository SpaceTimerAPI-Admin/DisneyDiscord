import discord
from discord import app_commands
import json
import difflib

async def register_slash_commands(client):
    @client.tree.command(name="request", description="Request a Disney dining alert")
    async def request(interaction: discord.Interaction):
        await interaction.response.send_message("🍽️ What restaurant are you looking for?", ephemeral=True)

        def check(m):
            return m.author == interaction.user and m.channel == interaction.channel

        try:
            msg = await client.wait_for("message", timeout=60.0, check=check)
            with open("restaurants.json") as f:
                data = json.load(f)
            names = [r["name"] for r in data]
            match = difflib.get_close_matches(msg.content, names, n=1)
            if not match:
                await interaction.followup.send("❌ No match found. Try again.", ephemeral=True)
                return
            restaurant = match[0]
            slug = next((r["slug"] for r in data if r["name"] == restaurant), None)
            await interaction.followup.send(f"✅ Found: **{restaurant}**. Now, what date? (YYYY-MM-DD)", ephemeral=True)

            msg2 = await client.wait_for("message", timeout=60.0, check=check)
            await interaction.followup.send(f"📆 Noted {msg2.content}. What time? (e.g. 6:00PM)", ephemeral=True)

            msg3 = await client.wait_for("message", timeout=60.0, check=check)
            await interaction.followup.send(f"⏰ Noted {msg3.content}. What party size?", ephemeral=True)

            msg4 = await client.wait_for("message", timeout=60.0, check=check)

            with open("requests.json", "r+", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                except:
                    data = {}
                user_id = str(interaction.user.id)
                entry = {
                    "restaurant": restaurant,
                    "slug": slug,
                    "date": msg2.content,
                    "time": msg3.content,
                    "party": msg4.content
                }
                data.setdefault(user_id, []).append(entry)
                f.seek(0)
                json.dump(data, f, indent=2)
                f.truncate()

            await interaction.followup.send(
                f"🎉 You’ll get alerts for {restaurant} on {msg2.content} at {msg3.content} for {msg4.content} guests!",
                ephemeral=True
            )
        except Exception as e:
            await interaction.followup.send("⏱️ Timed out or error. Try again.", ephemeral=True)

    await client.tree.sync()

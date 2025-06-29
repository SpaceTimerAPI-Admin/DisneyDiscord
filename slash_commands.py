import discord
from discord import app_commands
from discord.ext import tasks
import asyncio
from rapidfuzz import process
from restaurant_scraper import get_all_restaurants
import unicodedata
import re

# In-memory list of restaurants (original names) and their normalized forms for matching
latest_restaurants: list[str] = []
_latest_restaurants_norm: list[str] = []

def _normalize_name(name: str) -> str:
    """Normalize a restaurant name for fuzzy matching (remove accents, punctuation, case)."""
    # Remove diacritics (accents)
    name = unicodedata.normalize('NFD', name)
    name = ''.join(ch for ch in name if unicodedata.category(ch) != 'Mn')
    # Lowercase and replace common punctuation
    name = name.lower()
    for ch in ["’", "‘", "'"]:
        name = name.replace(ch, "")
    name = name.replace("&", "and")
    # Remove any other non-alphanumeric characters (except spaces and hyphens)
    name = re.sub(r'[^0-9a-z\- ]', '', name)
    # Collapse whitespace and hyphens
    name = name.strip()
    name = re.sub(r'\s+', ' ', name)
    name = re.sub(r'-+', '-', name)
    return name

@tasks.loop(minutes=60)
async def refresh_restaurants():
    """Background task to refresh the restaurant list every 60 minutes."""
    global latest_restaurants, _latest_restaurants_norm
    print("🔄 Refreshing restaurant list...", flush=True)
    try:
        # Fetch the list in a background thread to avoid blocking
        restaurants = await asyncio.get_running_loop().run_in_executor(None, get_all_restaurants)
        latest_restaurants = restaurants
        # Pre-compute normalized names for fuzzy matching
        _latest_restaurants_norm = [_normalize_name(name) for name in restaurants]
        print(f"✅ Loaded {len(latest_restaurants)} restaurants.", flush=True)
    except Exception as e:
        print(f"❌ Failed to refresh restaurants: {e}", flush=True)

async def setup_slash_commands(bot: discord.Client):
    """Register slash commands and start background tasks."""
    # Ensure the restaurant list is kept up-to-date
    if not refresh_restaurants.is_running():
        refresh_restaurants.start()

    # Define the /request slash command
    @bot.tree.command(name="request", description="Request a Disney dining reservation alert")
    async def request(interaction: discord.Interaction):
        """Interactively collect details for a dining alert request."""
        await interaction.response.defer(ephemeral=True)

        # Wait until restaurant list is loaded
        if not latest_restaurants:
            await interaction.followup.send("⏳ Restaurant list is still loading, please try again in a moment.")
            return

        # Question 1: Restaurant name
        await interaction.followup.send("🍽️ What **restaurant** are you looking for?")
        def check_msg(msg: discord.Message):
            return msg.author.id == interaction.user.id and msg.channel == interaction.channel

        try:
            user_msg = await bot.wait_for("message", check=check_msg, timeout=60)
        except asyncio.TimeoutError:
            await interaction.followup.send("⌛ Timeout. Please start over with `/request` when you’re ready.")
            return

        query = user_msg.content.strip()
        query_norm = _normalize_name(query)
        result = process.extractOne(query_norm, _latest_restaurants_norm)
        if not result:
            await interaction.followup.send("❌ I couldn't find any restaurant by that name. Please try `/request` again.")
            # Optionally delete the user's message to keep it private
            try: await user_msg.delete()
            except: pass
            return

        best_norm, score, index = result
        matched_name = latest_restaurants[index]
        if score < 80:
            # Suggest top 3 possible matches
            suggestions = process.extract(query_norm, _latest_restaurants_norm, limit=3)
            suggestion_names = [latest_restaurants[idx] for (_, _, idx) in suggestions if idx is not None]
            suggestion_text = "`, `".join(suggestion_names)
            await interaction.followup.send(f"🤔 Did you mean: `{suggestion_text}`? Please try again with the correct name.")
            # Clean up the user's message
            try: await user_msg.delete()
            except: pass
            return

        # We have a confident match
        chosen_restaurant = matched_name
        # Delete the user's restaurant message for privacy (optional)
        try: await user_msg.delete()
        except: pass

        # Question 2: Date
        await interaction.followup.send(f"✅ **{chosen_restaurant}** selected. On what **date**? (MM/DD/YYYY)")
        try:
            date_msg = await bot.wait_for("message", check=check_msg, timeout=60)
        except asyncio.TimeoutError:
            await interaction.followup.send("⌛ Timeout. Please start over with `/request`.")
            return

        date_str_input = date_msg.content.strip()
        from datetime import datetime
        try:
            # Parse date in MM/DD/YYYY format
            date_obj = datetime.strptime(date_str_input, "%m/%d/%Y")
        except ValueError:
            await interaction.followup.send("❌ Invalid date format. Please use MM/DD/YYYY and run `/request` again.")
            try: await date_msg.delete()
            except: pass
            return

        # Ensure the date is today or future
        today = datetime.today().date()
        if date_obj.date() < today:
            await interaction.followup.send("⚠️ That date is in the past. Please use a future date and run `/request` again.")
            try: await date_msg.delete()
            except: pass
            return

        # Format date as YYYY-MM-DD for checking
        date_str = date_obj.strftime("%Y-%m-%d")
        # Remove the user's date message for privacy
        try: await date_msg.delete()
        except: pass

        # Question 3: Time or time frame
        await interaction.followup.send("⏰ What **time** (or meal period) do you want to search for? "
                                        "e.g. `6:00 PM`, `Dinner`, `8 AM`")
        try:
            time_msg = await bot.wait_for("message", check=check_msg, timeout=60)
        except asyncio.TimeoutError:
            await interaction.followup.send("⌛ Timeout. Please start over with `/request`.")
            return

        time_query = time_msg.content.strip()
        # Parse the time input (supports "HH:MM AM/PM", "HH:MM" 24-hour, or keywords Breakfast/Lunch/Dinner)
        def parse_time_input(timestr: str) -> str or None:
            s = timestr.strip().lower()
            # Check meal period keywords
            if s in ["breakfast", "morning"]:
                return "0800"
            if s == "brunch":
                return "1030"
            if s in ["lunch", "afternoon"]:
                return "1200"
            if s in ["dinner", "evening", "night"]:
                return "1800"
            # Ensure space before am/pm if not provided (e.g., "6pm" -> "6 pm")
            if s.endswith("am") or s.endswith("pm"):
                if len(s) > 2 and s[-3] != ' ':
                    s = s[:-2] + ' ' + s[-2:]
                # Try 12-hour formats
                for fmt in ("%I:%M %p", "%I %p"):
                    try:
                        t = datetime.strptime(s, fmt)
                        return t.strftime("%H%M")
                    except ValueError:
                        continue
            # Try 24-hour formats
            try:
                if ":" in s:
                    t = datetime.strptime(s, "%H:%M")
                else:
                    t = datetime.strptime(s, "%H")
                return t.strftime("%H%M")
            except ValueError:
                return None

        time_param = parse_time_input(time_query)
        if time_param is None:
            await interaction.followup.send("❌ Unrecognized time format. Please try `/request` again with a time like `7:30 PM`.")
            try: await time_msg.delete()
            except: pass
            return

        # Remove the user's time message for privacy
        try: await time_msg.delete()
        except: pass

        # Everything collected: restaurant, date, time
        # Convert the restaurant name to URL slug format for checking
        def slugify(name: str) -> str:
            # Normalize accents and case
            n = unicodedata.normalize('NFD', name)
            n = ''.join(ch for ch in n if unicodedata.category(ch) != 'Mn').lower()
            # Remove special characters, replace spaces with hyphens
            for ch in ["’", "‘", "'"]:
                n = n.replace(ch, "")
            n = n.replace("&", "and")
            n = re.sub(r'[^0-9a-z\- ]', '', n).strip()
            n = re.sub(r'\s+', ' ', n)
            n = n.replace(' ', '-')
            n = re.sub(r'-+', '-', n).strip('-')
            return n

        restaurant_slug = slugify(chosen_restaurant)
        party_size = 2  # default party size (could be extended to ask user)

        # Register the alert request in the system (for background monitoring)
        try:
            import disney_checker
            disney_checker.add_alert(interaction.user.id, chosen_restaurant, restaurant_slug, date_str, time_param, party_size)
        except Exception as e:
            print(f"❌ Error adding alert: {e}", flush=True)
            await interaction.followup.send("⚠️ Failed to set up the alert. Please try again later.")
            return

        # Confirm to the user that their alert is set
        await interaction.followup.send(
            f"✅ Got it! I'll watch for openings at **{chosen_restaurant}** on **{date_str}** around **{time_query}**. "
            "You'll receive a DM with a booking link if a reservation becomes available. 🎉",
            ephemeral=True
        )

    # Sync the slash command with Discord
    await bot.tree.sync()

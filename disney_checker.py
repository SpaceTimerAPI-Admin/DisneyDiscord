from discord.ext import tasks
from playwright.sync_api import sync_playwright
import asyncio

# In-memory list of active alert requests
alerts = []  # each item: {"user_id": ..., "restaurant": ..., "slug": ..., "date": ..., "time": ..., "party": ...}

def add_alert(user_id: int, restaurant_name: str, restaurant_slug: str, date_str: str, time_str: str, party_size: int = 2):
    """Register a new alert request to monitor availability."""
    alert = {
        "user_id": user_id,
        "restaurant": restaurant_name,
        "slug": restaurant_slug,
        "date": date_str,
        "time": time_str,
        "party": party_size
    }
    alerts.append(alert)
    print(f"🔔 Alert added: {restaurant_name} on {date_str} at {time_str} for user {user_id}", flush=True)

@tasks.loop(minutes=5)
async def check_reservations_periodically(bot):
    """Background task that checks every 5 minutes for any reservation openings."""
    if not alerts:
        # No active alerts to check
        return
    print("🔍 Checking Disney Dining reservations for alerts...", flush=True)
    # We will check each active alert one by one
    for alert in list(alerts):
        restaurant = alert["restaurant"]
        slug = alert["slug"]
        date_str = alert["date"]
        time_str = alert["time"]
        party = alert["party"]
        user_id = alert["user_id"]

        # Construct the availability URL for this restaurant and criteria
        url = (f"https://disneyworld.disney.go.com/dining/{slug}/availability/?"
               f"partySize={party}&date={date_str}&time={time_str}")
        # Use Playwright in a background thread to load the page and check for openings
        def check_availability():
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto(url, timeout=60000)
                # Wait for a few seconds to allow availability results to load
                page.wait_for_timeout(5000)
                # Grab all available time texts (if any)
                times = page.locator(".available-time").all_text_contents()
                browser.close()
                return times

        try:
            times_available = await asyncio.get_running_loop().run_in_executor(None, check_availability)
        except Exception as e:
            print(f"❌ Error checking {restaurant}: {e}", flush=True)
            continue

        if times_available:
            # An opening is found!
            times_list = ", ".join(times_available)
            try:
                user = await bot.fetch_user(user_id)
                # Send a direct message to the user with the details and booking link
                await user.send(
                    f"🎉 **Reservation Alert:** A spot is available for **{restaurant}** on **{date_str}**!\n"
                    f"Available times: {times_list}\n"
                    f"👉 **Book now:** {url}\n\n*(This alert is for party size {party}. Grab it fast!)*"
                )
                print(f"✅ Alert sent to user {user_id} for {restaurant} on {date_str} at {times_list}", flush=True)
            except Exception as dm_error:
                print(f"❌ Could not DM user {user_id}: {dm_error}", flush=True)
            # Remove the alert after notifying to avoid duplicate alerts
            alerts.remove(alert)

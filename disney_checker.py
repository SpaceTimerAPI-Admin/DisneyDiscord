from discord.ext import tasks
from playwright.sync_api import sync_playwright
import os

def check_disney_reservation(restaurant_url_path, date="2025-07-15", time="1800", party_size=2):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        page.goto(f"https://disneyworld.disney.go.com/dining/{restaurant_url_path}/availability/", timeout=60000)

        page.select_option("#searchPartySize", str(party_size))
        page.fill("#searchDate", date)
        page.select_option("#searchTime", time)
        page.click(".button.search-cta")
        page.wait_for_timeout(5000)

        availability = page.locator(".available-time").all_text_contents()
        browser.close()
        return availability

@tasks.loop(minutes=5)
async def check_reservations_periodically(bot):
    print("🔍 Checking Disney Dining reservations... (simulated)")
    # You can trigger actual checks here and send alerts if integrated
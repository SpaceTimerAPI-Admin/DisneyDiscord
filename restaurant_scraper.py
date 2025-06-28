import asyncio
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from discord.ext import tasks

restaurant_names = []

def get_restaurants():
    return restaurant_names

async def scrape_restaurants():
    global restaurant_names
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto("https://disneyworld.disney.go.com/dining/")
        await page.wait_for_selector("ul.directory-list")

        content = await page.content()
        soup = BeautifulSoup(content, "html.parser")
        results = soup.select("ul.directory-list li a")

        names = []
        for a in results:
            name = a.text.strip()
            if name:
                names.append(name)

        restaurant_names = sorted(set(names))
        await browser.close()

@tasks.loop(hours=6)
async def start_restaurant_updater():
    await scrape_restaurants()

async def initial_scrape():
    await scrape_restaurants()
import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

URL = "https://disneyworld.disney.go.com/dining/"

async def _fetch_restaurants():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-setuid-sandbox",
                "--disable-gpu",
                "--single-process",
                "--no-zygote",
                "--disable-software-rasterizer",
                "--disable-features=site-per-process",
                "--enable-features=NetworkService,NetworkServiceInProcess"
            ]
        )
        page = await browser.new_page()
        await page.goto(URL, timeout=60000)
        await page.wait_for_selector(".cardName", timeout=60000)
        content = await page.content()
        await browser.close()
        return content

async def get_all_restaurants():
    html = await _fetch_restaurants()
    soup = BeautifulSoup(html, "html.parser")
    cards = soup.select(".cardName")
    restaurants = [card.get_text(strip=True) for card in cards]
    return restaurants

if __name__ == "__main__":
    restaurants = asyncio.run(get_all_restaurants())
    for name in restaurants:
        print(name)

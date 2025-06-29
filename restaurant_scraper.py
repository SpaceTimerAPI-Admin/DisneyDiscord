import asyncio
from playwright.async_api import async_playwright

async def get_all_restaurants():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto("https://disneyworld.disney.go.com/dining/", wait_until="networkidle")

        await page.wait_for_selector(".cardName", timeout=10000)
        elements = await page.query_selector_all(".cardName")
        restaurants = [await el.inner_text() for el in elements]

        await browser.close()
        return restaurants

if __name__ == "__main__":
    restaurants = asyncio.run(get_all_restaurants())
    for name in restaurants:
        print(name)
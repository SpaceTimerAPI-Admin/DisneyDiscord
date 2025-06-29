import os
import time
import requests
from bs4 import BeautifulSoup

SCRAPINGBEE_API_KEY = os.getenv("SCRAPINGBEE_API_KEY") or "EMEI1DXWK2PWVG79U2GH6AAWSSMX0N41S246I8TERDCODDVS6L6BLR2V1U197C26ND2UUYCS1L9XFKRH"
URL = "https://disneyworld.disney.go.com/dining/"

def _fetch_restaurants():
    print("⏳ Starting ScrapingBee request...")
    start = time.time()

    response = requests.get(
        "https://app.scrapingbee.com/api/v1/",
        params={
            "api_key": SCRAPINGBEE_API_KEY,
            "url": URL,
            "render_js": "true",
            "block_resources": "false",
            "stealth_proxy": "true"
        },
    )

    end = time.time()
    print(f"✅ ScrapingBee response received in {end - start:.2f} seconds")

    if response.status_code != 200:
        raise Exception(f"❌ ScrapingBee failed: {response.status_code} - {response.text}")
    
    return response.text

def get_all_restaurants():
    print("🔍 Parsing restaurant list...")
    start = time.time()

    html = _fetch_restaurants()

    # 💾 Save raw HTML for inspection
    with open("scrapingbee_output.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("📄 HTML content written to scrapingbee_output.html")

    soup = BeautifulSoup(html, "html.parser")

    # 🧪 Diagnostic logging: show divs and links
    print("\n🧪 Sample divs with classes:")
    for div in soup.find_all("div", class_=True)[:10]:
        print(" -", div.get("class"))

    print("\n🧪 Sample links (<a>):")
    for a in soup.find_all("a", href=True)[:10]:
        print(" -", a.get_text(strip=True), "|", a["href"])

    # 🧪 TEMP fallback: collect dining-related links
    cards = soup.select("a")
    restaurants = [
        card.get_text(strip=True)
        for card in cards
        if "dining" in card.get("href", "") and card.get_text(strip=True)
    ]

    end = time.time()
    print(f"\n✅ Parsed {len(restaurants)} possible restaurants in {end - start:.2f} seconds")
    return restaurants

if __name__ == "__main__":
    get_all_restaurants()

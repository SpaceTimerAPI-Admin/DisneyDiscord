import requests
from bs4 import BeautifulSoup
import json
import re

def scrape_and_save_restaurants():
    url = "https://disneyworld.disney.go.com/dining/"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    restaurants = []
    for a in soup.select("a.dining-landing-card-link"):
        name = a.get_text(strip=True)
        href = a.get("href")
        if name and href and "/dining/" in href:
            match = re.search(r"/dining/([a-z0-9-]+)/?$", href)
            slug = match.group(1) if match else None
            if slug:
                restaurants.append({"name": name, "slug": slug})

    with open("restaurants.json", "w", encoding="utf-8") as f:
        json.dump(restaurants, f, indent=2)
    print(f"✅ Scraped {len(restaurants)} restaurants.")

import requests
import time
import os

# This is Disney's JSON API endpoint for all dining locations
URL = "https://disneyworld.disney.go.com/cms/api/v4/disney-dining-locations/"

def get_all_restaurants():
    print("🔄 Fetching Disney dining JSON...")
    start = time.time()

    try:
        response = requests.get(URL)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"❌ Failed to fetch dining data: {e}")
        return []

    restaurants = [item["name"] for item in data if "name" in item]

    end = time.time()
    print(f"✅ Loaded {len(restaurants)} restaurants in {end - start:.2f} seconds")
    return restaurants

if __name__ == "__main__":
    for name in get_all_restaurants():
        print(name)

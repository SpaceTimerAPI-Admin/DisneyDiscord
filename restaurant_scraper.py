
import requests
from datetime import datetime

API_URL = "https://disneyworld.disney.go.com/finder/api/v1/explorer-service/list-ancestor-entities/wdw/80007798;entityType=destination/{date}/dining"

def get_all_restaurants():
    today = datetime.today().strftime("%Y-%m-%d")
    url = API_URL.format(date=today)
    print(f"🌐 Requesting Disney Dining API: {url}")
    response = requests.get(url, headers={"Accept": "application/json"})

    if response.status_code != 200:
        raise Exception(f"❌ Failed to fetch restaurants: {response.status_code} - {response.text}")

    data = response.json()
    restaurants = [entry["name"] for entry in data.get("entries", []) if "name" in entry]
    print(f"✅ Parsed {len(restaurants)} restaurants.")
    return restaurants

if __name__ == "__main__":
    all_restaurants = get_all_restaurants()
    for r in all_restaurants:
        print(r)

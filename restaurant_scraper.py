import requests
from datetime import datetime

# Disney World Dining API endpoint for listing all dining locations under the WDW destination
API_URL = ("https://disneyworld.disney.go.com/finder/api/v1/explorer-service/"
           "list-ancestor-entities/wdw/80007798;entityType=destination/{date}/dining")

def get_all_restaurants():
    """Fetches the list of all dining locations at Walt Disney World for the current date."""
    today = datetime.today().strftime("%Y-%m-%d")
    url = API_URL.format(date=today)
    print(f"🌐 Requesting Disney Dining API: {url}", flush=True)
    response = requests.get(url, headers={"Accept": "application/json"})
    if response.status_code != 200:
        raise Exception(f"❌ Failed to fetch restaurants: {response.status_code} - {response.text}")
    data = response.json()
    # Extract the name of each restaurant from the API response
    restaurants = [entry["name"] for entry in data.get("entries", []) if "name" in entry]
    print(f"✅ Parsed {len(restaurants)} restaurants.", flush=True)
    return restaurants

if __name__ == "__main__":
    # Test the scraper by printing all restaurant names
    for name in get_all_restaurants():
        print(name)

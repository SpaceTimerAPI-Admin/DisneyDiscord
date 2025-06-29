import requests
import datetime

DISNEY_DINING_API = (
    "https://disneyworld.disney.go.com/finder/api/v1/explorer-service/"
    "list-ancestor-entities/wdw/80007798;entityType=destination/{date}/dining"
)


def get_all_restaurants():
    today = datetime.date.today().isoformat()
    url = DISNEY_DINING_API.format(date=today)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    print(f"🌐 Requesting Disney Dining API: {url}")
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    data = response.json()

    restaurants = [entry["name"] for entry in data if "name" in entry]
    print(f"✅ Retrieved {len(restaurants)} restaurants from Disney API.")
    return restaurants


if __name__ == "__main__":
    all_names = get_all_restaurants()
    for name in all_names:
        print(name)

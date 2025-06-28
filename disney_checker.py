from discord.ext import tasks
from datetime import datetime
from playwright_checker import check_disney_reservation
import json

@tasks.loop(minutes=5)
async def check_reservations_periodically(client):
    print(f"🔍 Checking availability at {datetime.now()}")
    try:
        with open("requests.json", "r", encoding="utf-8") as f:
            requests = json.load(f)
    except:
        requests = {}

    for user_id, reqs in requests.items():
        for req in reqs:
            restaurant = req["restaurant"]
            slug = req["slug"]
            date = req["date"]
            time = req["time"]
            party = req["party"]

            available = check_disney_reservation(slug, date, time, party)
            if available:
                user = await client.fetch_user(int(user_id))
                if user:
                    await user.send(
                        f"🎉 Reservation found for **{restaurant}** on {date} at {time}!\n"
                        f"🔗 Book now: https://disneyworld.disney.go.com/dining/{slug}/availability/?partySize={party}&date={date}&time={time}"
                    )

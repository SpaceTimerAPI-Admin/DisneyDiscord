from playwright.sync_api import sync_playwright

def check_disney_reservation(restaurant_slug, date_str, time_str, party_size):
    url = f"https://disneyworld.disney.go.com/dining/{restaurant_slug}/availability/?partySize={party_size}&date={date_str}&time={time_str}"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, timeout=60000)
        page.wait_for_timeout(5000)
        found = page.query_selector("ul.availability-times")
        browser.close()
        return found is not None

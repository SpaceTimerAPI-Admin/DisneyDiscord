import requests
from bs4 import BeautifulSoup

def get_all_restaurants():
    url = "https://disneyworld.disney.go.com/dining/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    links = soup.select("a.dining-location-name")
    names = [link.get_text(strip=True) for link in links]
    return list(set(names))
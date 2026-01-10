import requests
from bs4 import BeautifulSoup

URL = "https://www.songkick.com/metro-areas/26794-australia-sydney"
page = requests.get(URL)

print(page.text)

soup = BeautifulSoup(page.content, "html.parser")

results = soup.find(id="metro-area-calendar")

print(results.prettify())

events = results.find_all("li", class_="event-listings-element")

for event in events:
    artist_tag = event.select_one("p.artists span")
    artist = artist_tag.get_text(strip=True)
    date = event.select_one("time")
    print(artist)
    print(date)

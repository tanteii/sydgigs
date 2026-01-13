import requests
from bs4 import BeautifulSoup
from dateutil import parser
from models.event import Event

BASE_URL = "https://www.songkick.com"
SONGKICK_URL = "https://www.songkick.com/metro-areas/26794-australia-sydney"

def scrape_songkick(page=1):

    URL = f"{SONGKICK_URL}?page={page}#metro-area-calendar"

    page = requests.get(URL, timeout=10)
    soup = BeautifulSoup(page.content, "html.parser")

    results = soup.find(id="metro-area-calendar")
    parsed_events = []

    events = results.find_all("li", class_="event-listings-element")
    for event in events:
        artist_tag = event.select_one("p.artists span")
        artist = artist_tag.get_text(strip=True)

        date_tag = event.select_one("time")
        # date = date_tag["datetime"]
        date = parser.parse(date_tag["datetime"])

        venue_tag = event.select_one("p.location span")
        venue = venue_tag.get_text(strip=True)

        link_tag = event.select_one("a")
        link = BASE_URL + link_tag["href"]


        # print(artist)
        # print(date)
        # print(venue)
        # print(link)
        # print()

        parsed_events.append(Event(
            artist = artist,
            date = date,
            venue = venue,
            url = link,
            source = "Songkick"
        ))

    return parsed_events

import requests
from bs4 import BeautifulSoup
from dateutil import parser
from models.event import Event

BASE_URL = "https://www.songkick.com"
SONGKICK_URL = "https://www.songkick.com/metro-areas/26794-australia-sydney"

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

def scrape_songkick(page=1):

    URL = f"{SONGKICK_URL}?page={page}#metro-area-calendar"
    print(URL)
    page = requests.get(URL, headers=headers, timeout=10)
    soup = BeautifulSoup(page.content, "html.parser")

    parsed_events = []

    # print(soup)

    events = soup.select("li.event-listings-element")
    for event in events:
        artists_tag = event.select_one("p.artists")
        if not artists_tag:
            continue

        main_artist_tag = artists_tag.select_one("strong")
        main_artist = main_artist_tag.get_text(strip=True) if main_artist_tag else ""

        supporting_artist_tag = artists_tag.select_one("span.support")
        supporting_artist = supporting_artist_tag.get_text(strip=True) if supporting_artist_tag else ""
        
        artist = f"{main_artist} (with {supporting_artist})" if supporting_artist else main_artist

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

import requests
import aiohttp
from bs4 import BeautifulSoup
from dateutil import parser as dateparser
from models.event import Event

BASE_URL = "https://www.songkick.com"
SONGKICK_URL = "https://www.songkick.com/metro-areas/26794-australia-sydney"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

SOURCE_NAME = "Songkick"

async def scrape_songkick(session: aiohttp.ClientSession, page: int = 1):

    url = f"{SONGKICK_URL}?page={page}#metro-area-calendar"

    try:
        async with session.get(url, headers=HEADERS, timeout=aiohttp.ClientTimeout(total=15)) as resp:
            if resp.status != 200:
                return []
            html = await resp.text()
    except Exception:
        return []

    # page = requests.get(URL, headers=headers, timeout=10)
    soup = BeautifulSoup(html, "html.parser")
    events = []

    for li in soup.select("li.event-listings-element"):
        try:
            event = parse_event(li)
            if event:
                events.append(event)
        except Exception:
            continue

    return events

def parse_event(li):
    artists_tag = li.select_one("p.artists")
    if not artists_tag:
        return None

    main_tag = artists_tag.select_one("strong")
    if not main_tag:
        return None
    artist = main_tag.get_text(strip=True)

    # optional supporting artists
    support_tag = artists_tag.select_one("span.support")
    supporting = support_tag.get_text(strip=True) if support_tag else None
    # strip common prefixes
    if supporting:
        for prefix in ("with ", "feat. ", "ft. ", "+ "):
            if supporting.lower().startswith(prefix):
                supporting = supporting[len(prefix):]
                break

    date_tag = li.select_one("time")
    if not date_tag or not date_tag.get("datetime"):
        return None
    date_tz = dateparser.parse(date_tag["datetime"])
    date = date_tz.replace(tzinfo=None)

    venue_tag = li.select_one("p.location span")
    venue = venue_tag.get_text(strip=True) if venue_tag else "TBA"

    link_tag = li.select_one("a")
    link = (BASE_URL + link_tag["href"]) if link_tag and link_tag.get("href") else BASE_URL

    # Songkick sometimes includes it as a class on the li or a data attribute
    genre_tag = li.select_one("p.genres") or li.select_one("[class*='genre']")
    genre = genre_tag.get_text(strip=True) if genre_tag else None


        # print(artist)
        # print(date)
        # print(venue)
        # print(link)
        # print()

    return Event(
        artist = artist,
        date = date,
        venue = venue,
        url = link,
        source = SOURCE_NAME,
        supporting=supporting,
        genre=genre,
    )


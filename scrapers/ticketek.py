import aiohttp
from bs4 import BeautifulSoup
from dateutil import parser as dateparser
from models.event import Event

BASE_URL = "https://premier.ticketek.com.au"
TICKETEK_URL = "https://premier.ticketek.com.au/shows/genre.aspx?c=2048&r=NSW"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

SOURCE_NAME = "Ticketek"

async def scrape_ticketek(session: aiohttp.ClientSession, page: int = 1):

    url = f"{TICKETEK_URL}?page={page}#metro-area-calendar"

    try:
        async with session.get(url, headers=HEADERS, timeout=aiohttp.ClientTimeout(total=15)) as resp:
            if resp.status != 200:
                return []
            html = await resp.text()
    except Exception:
        return []

    soup = BeautifulSoup(html, "html.parser")
    events = []

    for item in soup.select("div.show-item, li.show, article.event"):
        try:
            event = parse_event(item)
            if event:
                events.append(event)
        except Exception:
            continue

    return events

def parse_event(item):
    title_tag = item.select_one("h2, h3, .show-title, .event-title")
    if not title_tag:
        return None
    artist = title_tag.get_text(strip=True)



    print(artist)
    # print(date)

    return Event(
        artist=artist,
        # date=date,
        # venue=venue,
        # url=url,
        source=SOURCE_NAME,
    )
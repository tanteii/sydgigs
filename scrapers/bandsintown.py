# scrapers/bandsintown.py

import asyncio
from datetime import datetime, timedelta, timezone
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from models.event import Event

BASE_URL = "https://www.bandsintown.com/c/sydney-australia/choose-dates/genre/all-genres"
SOURCE_NAME = "Bandsintown"


def build_url(date: datetime) -> str:
    day_start = date.strftime("%Y-%m-%dT00:00:00")
    day_end = date.strftime("%Y-%m-%dT23:00:00")
    return (
        f"{BASE_URL}?calendarTrigger=false"
        f"&date={day_start}%2C{day_end}"
    )


async def scrape_day(page, date: datetime) -> list[Event]:
    url = build_url(date)
    try:
        await page.goto(url, timeout=20000, wait_until="domcontentloaded")
        await page.wait_for_selector("a[href*='/e/']", timeout=10000)
    except Exception:
        # no events (for this day) or timeout
        return []

    soup = BeautifulSoup(await page.content(), "html.parser")
    events = []

    # Bandsintown uses hashed classnames
    # Concert info stored deep in a[href="/e/..."] structure
    # card = <a href="/e/...">
    for card in soup.select("a[href*='/e/']"):
        try:
            event = parse_card(card, date)
            if event:
                events.append(event)
        except Exception:
            continue

    return events


def parse_card(card, date) -> Event | None:
    # img alt is stable (never hashed) and stores artist name
    # img = card.select_one("img[alt]:not([alt='calendarIcon']):not([alt='peopleIcon'])")
    # if not img:
    #     return None
    # artist = img["alt"]

    # venue/date text in leaf <div> elements
    text_divs = [d.get_text(strip=True) for d in card.select("div")
                 if d.get_text(strip=True) and not d.find("div")]
    # example text_divs: [artist, venue, date]
    artist = text_divs[0] if text_divs else None
    venue = text_divs[1] if len(text_divs) > 1 else "TBA"
    raw_date = text_divs[2] if len(text_divs) > 2 else ""

    # parse date + year from query
    try:
        from dateutil import parser as dp
        event_date = dp.parse(f"{raw_date} {date.year}")
    except Exception:
        event_date = date

    # URL
    url = card["href"]

    print(artist)
    print(event_date)
    print(venue)
    print(url)

    return Event(
        artist=artist,
        date=event_date,
        venue=venue,
        url=url,
        source=SOURCE_NAME,
    )


async def scrape_bandsintown(
    session,                        # unused (kept for interface consistency)
    page_num: int = 1,              # unused (date-based pagination)
    date_from: datetime | None = None,
    date_to:   datetime | None = None,
):
    now = datetime.now(timezone.utc)
    search_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
    search_date += timedelta(days=page_num)

    all_events = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            locale="en-AU",
            timezone_id="Australia/Sydney",
        )
        page = await context.new_page()

        print(f"[bandsintown] Scraping days ({search_date})")

        day_events = await scrape_day(page, search_date)
        print(f"[bandsintown] {search_date} events")
        all_events.extend(day_events)
        await asyncio.sleep(0.5)

        await browser.close()

    return all_events
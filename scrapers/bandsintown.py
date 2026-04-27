# scrapers/bandsintown.py

import asyncio
from datetime import datetime, timedelta, timezone
from playwright.async_api import async_playwright, Browser, Page
from bs4 import BeautifulSoup
from models.event import Event

BASE_URL = "https://www.bandsintown.com/c/sydney-australia/choose-dates/genre/all-genres"
SOURCE_NAME = "Bandsintown"
DAYS_PER_PAGE = 1


# def build_url(date_from, date_to):
#     start = date_from.strftime("%Y-%m-%dT00:00:00")
#     end = date_to.strftime("%Y-%m-%dT23:00:00")
#     return f"{BASE_URL}?calendarTrigger=false&date={start}%2C{end}"

# convert page no. to date window (interface consistency)
def page_to_window(page_num: int):
    now = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    offset = (page_num - 1) * DAYS_PER_PAGE

    current = now + timedelta(days=offset)
    end = current + timedelta(days=DAYS_PER_PAGE - 1)

    while current <= end:
        yield current
        current += timedelta(days=1)

# persistent browser state
playwright = None
browser: Browser | None = None
page: Page | None = None

async def get_page():
    global playwright, browser, page
    if page is None:
        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(headless=True)
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

    return page

async def close_browser():
    global playwright, browser, page
    if browser:
        await browser.close()
        browser = None
        page = None
    if playwright:
        await playwright.stop()
        playwright = None

async def scrape_window(page, date):
    start = date.strftime("%Y-%m-%dT00:00:00")
    end = date.strftime("%Y-%m-%dT23:59:59")
    url = f"{BASE_URL}?calendarTrigger=false&date={start}%2C{end}"
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

    return Event(
        artist=artist,
        date=event_date,
        venue=venue,
        url=url,
        source=SOURCE_NAME,
    )


async def scrape_bandsintown(
    session, # unused (kept for interface consistency)
    page_num: int = 1,
):
    """
    page_num corresponds to a set date window
    Browser kept alive over calls for efficiency
    """
    dates = list(page_to_window(page_num))
    print(f"[bandsintown] Scraping {len(dates)} days ({dates[0]} -> {dates[-1]})")

    page = await get_page()

    all_events = []

    # scrape by individual dates
    # site requires authentication for extended concert viewing
    for date in dates:
        events = await scrape_window(page, date)
        all_events.extend(events)
        await asyncio.sleep(0.5)

    return all_events

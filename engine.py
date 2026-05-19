import asyncio
import aiohttp
from scrapers import SCRAPERS
from models.event import Event
from dateutil import parser as dateparser
from scrapers import bandsintown

SOURCE_CONFIG = {
    "bandsintown": {"days_per_page": 2},
    "songkick": {"days_per_page": 6},
}

class ScrapingEngine:
    """
    Async multi-source scraping engine.

    Fetches pages from multiple sources concurrently using asyncio + aiohttp or Playwright,
    normalises results into Event objects, and deduplicates across sources.
    """

    def __init__(self, sources: list[str] | None = None, chunk: int | int = 10):
        self.sources = sources or list(SCRAPERS.keys())
        self.chunk: int = chunk
        self.seen: set[tuple] = set()
        self.cache: list[Event] = []
        self.page: int = 1
        self.exhausted: set[str] = set()

    def reset(self):
        self.seen.clear()
        self.cache.clear()
        self.page = 1
        self.exhausted.clear()

    async def fetch_page(self, page, sources=None):
        """
        Concurrently fetch one page from all given sources (all sources by default).
        """
        if not sources:
            sources = self.sources
        
        active = [s for s in sources if s not in self.exhausted]
        if not active:
            return []

        async with aiohttp.ClientSession() as session:
            # call scraper coroutine for each source
            tasks = [
                SCRAPERS[source](session, page)
                for source in active
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)

        new_events = []
        for source, result in zip(active, results):
            if isinstance(result, Exception):
                self.exhausted.add(source)
                continue
            if not result:
                continue
            for event in result:
                key = event.key()
                if key not in self.seen:
                    self.seen.add(key)
                    new_events.append(event)

        # sort by date ascending
        new_events.sort(key=lambda e: e.date)
        self.cache.extend(new_events)
        return new_events
    
    # fetch next page of entries and return cache
    async def fetch_next(self):
        if not self.depleted:
            await self.fetch_page(self.page)

        self.page += 1
        return list(self.cache)

    # fetch specified no. pages from all sources
    async def fetch_all(self, max_pages: int = 5) -> list[Event]:
        for _ in range(max_pages):
            if self.depleted:
                break
            await self.fetch_page(self.page)

            self.page += 1

        return list(self.cache)
    
    async def fetch_filtered(self, filters):
        index = 0
        while True:
            filtered = apply_filters(self.cache, filters)
            slice = filtered[index:index+self.chunk]

            # check lagging sources
            missing = check_common_dates(self.cache, self.sources)
            # scrape until enough entries for page or sources exhausted
            while (len(slice) < self.chunk or missing) and not self.depleted:
                # scrape sources with missing/lagging dates for catchup
                # (ensure consistent, interleaved sources in output)
                if missing:
                    await self.fetch_page(self.page, missing)
                else:
                    await self.fetch_page(self.page, self.sources)

                self.page += 1
                filtered = apply_filters(self.cache, filters)
                filtered.sort(key=lambda e: e.date)
                slice = filtered[index:index+self.chunk]

                # recompute missing post-fetch
                missing = check_common_dates(self.cache, self.sources)


            # no more entries
            if not slice:
                return
            
            yield slice
            index += len(slice)

            if self.depleted and index >= len(filtered):
                return


    # close persistent Playwright browsers
    async def close(self):
        await bandsintown.close_browser()

    @property
    def depleted(self):
        return len(self.exhausted) >= len(self.sources)
    
    @property
    def cached(self):
        return list(self.cache)
    
# ensure same dates have been scraped for all sources (due to page display mismatch)
# returns sources with missing events
def check_common_dates(cache, sources):
    if not cache:
        return []
    
    # latest date per source
    latest_per_src = {}
    for event in cache:
        src = event.source.lower()
        date = event.date.date()
        if src not in latest_per_src or date > latest_per_src[src]:
            latest_per_src[src] = date

    if not latest_per_src:
        return []
    
    # latest date scraped amongst all sources
    latest = max(latest_per_src.values())

    missing = []
    for source in sources:
        s = source.lower()

        # events do not exist for source -> scrape
        if s not in latest_per_src:
            missing.append(s)
            continue
        
        # events lag behind by a page -> scrape
        src_config = SOURCE_CONFIG.get(s, {"days_per_page": 0})
        lag = (latest - latest_per_src[s]).days

        if lag > src_config["days_per_page"]:
            missing.append(s)

    return missing


def apply_filters(
    events: list[Event],
    filters: dict[str, any]
):
    """Filter a list of events. All filters are case-insensitive substrings."""
    artist = filters['artist']
    venue = filters['venue']
    source = filters['source']
    date_from = filters['date_from']
    date_to = filters['date_to']

    filtered = events

    if artist:
        q = artist.lower()
        filtered = [
            e for e in filtered
            if q in e.artist.lower() or (e.supporting and q in e.supporting.lower())
        ]

    if venue:
        q = venue.lower()
        filtered = [e for e in filtered if q in e.venue.lower()]

    if source:
        filtered = [e for e in filtered if e.source.lower() == source.lower()]

    if date_from:
        try:
            from_dt = dateparser.parse(date_from)
            filtered = [e for e in filtered if e.date >= from_dt]
        except Exception:
            pass

    if date_to:
        try:
            to_dt = dateparser.parse(date_to)
            filtered = [e for e in filtered if e.date <= to_dt]
        except Exception:
            pass

    return filtered
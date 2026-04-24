import asyncio
import aiohttp
from scrapers import SCRAPERS
from models.event import Event

class ScrapingEngine:
    """
    Async multi-source scraping engine.

    Fetches pages from multiple sources concurrently using asyncio + aiohttp,
    normalises results into Event objects, and deduplicates across sources.
    """

    def __init__(self, sources: list[str] | None = None):
        self.sources = sources or list(SCRAPERS.keys())
        self.seen: set[tuple] = set()
        self.cache: list[Event] = []
        self.page: int = 1
        self.exhausted: set[str] = set()

    def reset(self):
        self.seen.clear()
        self.cache.clear()
        self.page = 1
        self.exhausted.clear()

    async def fetch_page(self, page):
        """
        Concurrently fetch one page from all active sources.
        """
        active = [s for s in self.sources if s not in self.exhausted]
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
            if isinstance(result, Exception) or not result:
                self.exhausted.add(source)
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
    
    # fetch next page, increment page counter
    async def fetch_next(self):
        events = await self.fetch_page(self.page)
        self.page += 1
        return events

    # fetch specified no. pages from all sources
    async def fetch_all(self, max_pages: int = 5) -> list[Event]:
        """Eagerly fetch up to max_pages pages from all sources."""
        for _ in range(max_pages):
            batch = await self.fetch_next()
            if not batch:
                break
        return list(self.cache)
    
    @property
    def undepleted(self):
        return len(self.exhausted) < len(self.sources)
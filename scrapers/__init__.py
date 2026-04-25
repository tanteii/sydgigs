from scrapers.songkick import scrape_songkick
from scrapers.ticketek import scrape_ticketek

SCRAPERS = {
    "songkick": scrape_songkick,
    "ticketek": scrape_ticketek,
}

__all__ = ["SCRAPERS", "scrape_songkick", "scrape_ticketek"]
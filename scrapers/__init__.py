from scrapers.songkick import scrape_songkick
from scrapers.bandsintown import scrape_bandsintown

SCRAPERS = {
    "songkick": scrape_songkick,
    "bandsintown": scrape_bandsintown,
}

__all__ = ["SCRAPERS", "scrape_songkick", "scrape_bandsintown"]
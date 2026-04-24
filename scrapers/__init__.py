from scrapers.songkick import scrape_songkick

SCRAPERS = {
    "songkick": scrape_songkick,
}

__all__ = ["SCRAPERS", "scrape_songkick"]
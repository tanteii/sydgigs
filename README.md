# Concert Scraper
This project enables viewing, searching and filtering of normalised live music events happening in Sydney by scraping public event websites and normalising data into a consistent format.

Live concert information are never limited to singular platforms/venues, making it difficult to completely view all upcoming events in one place, particularly for less mainstream or non-English performers. 
This project addresses this problem by aggregating and standardising concert data from various sources into a single dataset for easy queries and filtering.

**How does it work.**
The system will be built under a modular scraper pipeline:
* Each supported concert data source has its own scraper module for fetching and parsing event data.
* Scraped data is converted into a shared model for consisnte fields.
* Normalised events are stored locally for further querying and filtering.
This supports the addition of sources without modifying existing scrapers.

**How to run.**
Within repository directory,

**Usage**

```bash
python main.py                              # start web UI (default)

python main.py --cli                        # paginated terminal output

python main.py --cli --artist tame          # filter by artist in CLI mode (--help for more filters)

python main.py --export csv                 # dump all events to stdout as CSV

python main.py --export csv -o file.csv     # save all events to file

python main.py --export json -o file.json   # save all events to file
```

**Planned improvements.**
* Adding more concert sources
* More filters
* Persistent data / Database
* Simple web interface
* Scheduled scraping/updates

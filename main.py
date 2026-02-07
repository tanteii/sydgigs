from scrapers.songkick import scrape_songkick
import argparse

SCRAPERS = {
    "songkick": scrape_songkick,
    # "ticketek": scrape_ticketek
}

seen_events = set()

def main():
    parser = argparse.ArgumentParser()
    
    parser.add_argument(
        "-c", "--chunk",
        type=int,
        default=5,
        help="Number of events displayed per page"
    )

    parser.add_argument(
        "-s", "--sources",
        nargs="+",
        choices=SCRAPERS.keys(),
        default=["songkick"],
        help="Sources to be scraped"
    )

    args = parser.parse_args()

    scraper(event_chunk=args.chunk, sources=args.sources)

# Scrape events from websites and display in a paged and normalised format
def scraper(event_chunk=5, sources=None):
    display_page = 1

    web_page = 1

    event_index = 0
    all_events = []
    new_events = []

    scrapers = [SCRAPERS[source] for source in sources]

    while True:
        print(f"\n--- Page {display_page} ---")

        # Scrape new events if none to display
        if event_index + event_chunk > len(all_events):
            for scrape in scrapers:
                new_events = scrape(web_page)
                all_events = append_events(all_events, new_events)
                web_page += 1
        
        if not new_events:
            print("No more events found")
            break
        
        # Limit displayed events per page
        end = min(event_index + event_chunk, len(all_events))
        for i in range(event_index, end):
            print(all_events[i])
            print()
        

        user_input = input("Press [Enter] to load more\nor [q] to quit\n").strip().lower()

        if user_input == "q":
            print("Quitting.")
            break
            
        event_index += event_chunk
        display_page += 1

    return all_events

# Append new events with deduplication across pages
def append_events(events, new_events):
    for event in new_events:
        key = event.key()
        if key not in seen_events:
            seen_events.add(key)
            events.append(event)

    return events

if __name__ == "__main__":
    main()
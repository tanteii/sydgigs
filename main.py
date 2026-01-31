from scrapers.songkick import scrape_songkick

def main():
    scraper()

seen_events = set()

def scraper():
    display_page = 1

    web_page = 1
    event_chunk = 5

    event_index = 0
    all_events = []
    new_events = []

    while True:
        print(f"\n--- Page {display_page} ---")
        if event_index + event_chunk > len(all_events):
            new_events = scrape_songkick(web_page)
            # all_events.extend(new_events)
            all_events = append_events(all_events, new_events)
            web_page += 1
        
        

        if not new_events:
            print("No more events found")
            break
        
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

def append_events(events, new_events):
    for event in new_events:
        key = event.key()
        if key not in seen_events:
            seen_events.add(key)
            events.append(event)

    return events

if __name__ == "__main__":
    main()
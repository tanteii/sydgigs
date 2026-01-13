from scrapers.songkick import scrape_songkick

def main():
    scraper()


def scraper():
    page = 1
    all_events = []

    while True:
        print(f"\n--- Page {page} ---")
        events = scrape_songkick(page)

        if not events:
            print("No more events found")
            break

        for event in events:
            print(event)
            print()

        user_input = input("Press [Enter] to load more\nor [q] to quit\n").strip().lower()

        if user_input == "q":
            print("Quitting.")
            break
            
        page += 1

    return all_events

if __name__ == "__main__":
    main()
from scrapers.songkick import scrape_songkick

def main():
    events = scrape_songkick()
    for event in events:
        print(event)
        print()

if __name__ == "__main__":
    main()
"""
main.py — CLI entrypoint for Sydney Gigs Scraper.

Usage:
    python main.py                              # start web UI (default)
    python main.py --cli                        # paginated terminal output
    python main.py --export csv                 # dump all events to stdout as CSV (JSON supported)
    python main.py --export csv -o file.csv     # dump all events to file.csv as CSV
"""

import argparse
import asyncio
import sys
from engine import ScrapingEngine


def cli_mode(args):
    engine = ScrapingEngine(sources=args.sources)
    chunk = args.chunk
    display_page = 1

    async def run():
        nonlocal display_page
        while True:
            print(f"\n--- Page {display_page} ---")
            new = await engine.fetch_next()

            if not new and not engine.undepleted:
                print("No more events found.")
                break

            for i, event in enumerate(new[:chunk]):
                print(event)
                print()

            if not engine.undepleted:
                print("— End of results —")
                break

            user_input = input("Press [Enter] for more, or [q] to quit\n").strip().lower()
            if user_input == "q":
                break

            display_page += 1

    asyncio.run(run())


def main():
    parser = argparse.ArgumentParser(
        description="Concert Scraper — async multi-source concert scraper"
    )
    
    parser.add_argument(
        "--cli", 
        action="store_true", 
        help="Run in terminal mode instead of web UI"
    )

    parser.add_argument(
        "-c", "--chunk",
        type=int,
        default=5,
        help="Number of events displayed per page"
    )

    parser.add_argument(
        "-s", "--sources",
        nargs="+",
        choices=["songkick"],
        default=["songkick"],
        help="Sources to be scraped"
    )

    parser.add_argument(
        "--export", 
        choices=["json", "csv"], 
        help="Export all events and exit to stdout"
    )

    parser.add_argument(
        "-o", "--output", 
        type=str,
        default=None,
        help="Optional file to export data to (default: stdout)"
    )

    args = parser.parse_args()

    # export events to json/csv based on args
    if args.export:
        print("Now exporting... (10 pages)")
        async def dump():
            engine = ScrapingEngine(sources=args.sources)
            await engine.fetch_all(max_pages=10)
            events = engine.cache

            output_target = (
                open(args.output, "w", newline="", encoding="utf-8") 
                if args.output else sys.stdout
            )

            if args.export == "json":
                import json
                json.dump([e.to_dict() for e in events], 
                            output_target, indent=2, default=str)
            else:
                import csv
                w = csv.DictWriter(output_target, fieldnames=["artist", "supporting",
                                   "date_display", "time_display", "venue", "source", "url"])
                w.writeheader()
                for e in events:
                    d = e.to_dict()
                    w.writerow({k: d.get(k, "") for k in w.fieldnames})

            if args.output:
                output_target.close()
            
        asyncio.run(dump())
        return


    if args.cli:
        cli_mode(args)
    # else:
        # TBA web mode

if __name__ == "__main__":
    main()
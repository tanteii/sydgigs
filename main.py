"""
main.py — CLI entrypoint for SydGigs Scraper.

Usage:
    python main.py                              # start web UI (default)
    python main.py --cli                        # paginated terminal output
    python main.py --cli --artist tame          # filter by artist in CLI mode
    python main.py --export csv                 # dump all events to stdout as CSV (JSON supported)
    python main.py --export csv -o file.csv     # dump all events to file.csv as CSV
"""

import argparse
import asyncio
import sys
import json
import csv
from server import app
from engine import ScrapingEngine, apply_filters


def cli_mode(args):
    chunk = args.chunk
    filters = to_filters(args)
    engine = ScrapingEngine(sources=args.sources, chunk=chunk)

    async def run():
        try:
            display_page = 1
            async for filtered in engine.fetch_filtered(filters=filters):
                if not filtered and engine.depleted:
                        print("No more events found.")
                        break
        
                print(f"\n--- Page {display_page} ---")
                # filtered.sort(key=lambda e: e.date)
                for event in filtered:
                    print(event)
                    print()

                display_page += 1

                if engine.depleted:
                    print("— End of results —")
                    break

                user_input = input("Press [Enter] for more, or [q] to quit\n").strip().lower()
                if user_input == "q":
                    break

        finally:
            await engine.close()

    asyncio.run(run())

def web_mode():
    print("Starting Sydney Gigs web interface at http://localhost:5000")
    app.run(debug=False, port=5000)

def to_filters(args):
    return {
        'artist': args.artist,
        'venue': args.venue,
        'date_from': args.date_from,
        'date_to': args.date_to,
        'source': args.source
    }


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
        choices=["songkick", "bandsintown"],
        default=["songkick", "bandsintown"],
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

    # filter options
    parser.add_argument("--artist", type=str, default="", help="Filter by artist name")
    parser.add_argument("--venue", type=str, default="", help="Filter by venue name")
    parser.add_argument("--date-from", dest="date_from", type=str, default="", help="Start date filter")
    parser.add_argument("--date-to", dest="date_to", type=str, default="", help="End date filter")
    parser.add_argument("--source", type=str, default="", help="Filter by source (songkick/ticketek)")

    args = parser.parse_args()

    # export events to json/csv based on args
    if args.export:
        print("Now exporting... (10 pages)")
        async def dump():
            engine = ScrapingEngine(sources=args.sources)
            try:
                await engine.fetch_all(max_pages=10)
                events = apply_filters(engine.cached, to_filters(args))
                events.sort(key=lambda e: e.date)

                output_target = (
                    open(args.output, "w", newline="", encoding="utf-8") 
                    if args.output else sys.stdout
                )

                if args.export == "json":
                    json.dump([e.to_dict() for e in events], 
                                output_target, indent=2, default=str)
                else:
                    w = csv.DictWriter(output_target, fieldnames=["artist", "supporting",
                                    "date_display", "time_display", "venue", "source", "url"])
                    w.writeheader()
                    for e in events:
                        d = e.to_dict()
                        w.writerow({k: d.get(k, "") for k in w.fieldnames})

                if args.output:
                    output_target.close()
            finally:
                await engine.close()
            
        asyncio.run(dump())
        return


    if args.cli:
        cli_mode(args)
    else:
        web_mode()

if __name__ == "__main__":
    main()
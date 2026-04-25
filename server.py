import asyncio
from flask import Flask, jsonify, request, render_template
from engine import ScrapingEngine, apply_filters

app = Flask(__name__)

# engine instance per server run, holds deduplicated cache
engine = ScrapingEngine(sources=["songkick"])

# create event loop for asynchronous scraper calls
def run_async(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/events")
def get_events():
    """
    GET /api/events
    """
    load_more = request.args.get("load_more", "false").lower() == "true"

    # fetch a new page from the web if requested or cache is empty
    if load_more or not engine.cached:
        run_async(engine.fetch_next())

    # apply filters to the full in-memory cache
    events = apply_filters(
        engine.cached,
        artist=request.args.get("artist", ""),
        venue=request.args.get("venue", ""),
        date_from=request.args.get("date_from", ""),
        date_to=request.args.get("date_to", ""),
        source=request.args.get("source", ""),
    )

    return jsonify({
        "events": [e.to_dict() for e in events],
        "total": len(events),
        "sources": list(engine.sources),
    })

if __name__ == "__main__":
    app.run(debug=True, port=5000)

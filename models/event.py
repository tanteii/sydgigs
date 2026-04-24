from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Event:
    artist: str
    date: datetime
    venue: str
    url: str
    source: str
    supporting: Optional[str] = field(default=None)
    genre: Optional[str] = field(default=None)

    # event uniquely identified by artist+date+venue
    def key(self):
        return (self.artist.lower(), self.date.date(), self.venue.lower())

    def to_dict(self):
        return {
            "artist": self.artist,
            "supporting": self.supporting,
            "date": self.date.isoformat(),
            "date_display": self.date.strftime("%a %d %b %Y"),
            "time_display": self.date.strftime("%I:%M %p").lstrip("0"),
            "venue": self.venue,
            "url": self.url,
            "source": self.source,
            "genre": self.genre,
        }

    def __str__(self):
        support_line = f"  w/ {self.supporting}\n" if self.supporting else ""
        return (
            f"{self.artist}\n"
            f"{support_line}"
            f"  {self.venue}\n"
            f"  {self.date.strftime('%a %d %b %Y, %I:%M %p')}\n"
            f"  {self.url} ({self.source})"
        )

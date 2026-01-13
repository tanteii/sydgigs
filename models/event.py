from dataclasses import dataclass
from datetime import datetime

@dataclass
class Event:
    artist: str
    date: datetime
    venue: str
    url: str
    source: str

    def __str__(self):
        return (
            f"{self.artist}\n"
            f"Location: {self.venue}\n"
            f"Date:  {self.date.strftime('%d %b %Y, %I:%M %p')}\n"
            f"Link: {self.url}\n"
            f"({self.source})"
        )

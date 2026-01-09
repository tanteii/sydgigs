from dataclasses import dataclass
from datetime import datetime

@dataclass
class Event:
    artist: str
    date: datetime
    venue: str
    url: str
    source: str

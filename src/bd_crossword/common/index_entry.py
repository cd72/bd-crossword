

from dataclasses import dataclass
from datetime import date
from datetime import datetime


@dataclass
class IndexEntry:
    page_date: date
    title: str
    url: str
    hints_author: str
    difficulty: int
    enjoyment: int
    last_updated: datetime

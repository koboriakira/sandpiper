from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class EventCategory(Enum):
    WORK = "仕事"
    PRIVATE = "プライベート"
    TJPW = "TJPW"


@dataclass
class CalendarEvent:
    name: str
    category: EventCategory
    start_datetime: datetime
    end_datetime: datetime


@dataclass
class InsertedCalendarEvent:
    id: str
    name: str
    category: EventCategory
    start_datetime: datetime
    end_datetime: datetime

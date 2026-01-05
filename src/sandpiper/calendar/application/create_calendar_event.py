from dataclasses import dataclass
from datetime import datetime

from sandpiper.calendar.domain.calendar_event import CalendarEvent, EventCategory, InsertedCalendarEvent
from sandpiper.calendar.domain.calendar_repository import CalendarRepository


@dataclass
class CreateCalendarEventRequest:
    name: str
    category: EventCategory
    start_datetime: datetime
    end_datetime: datetime


@dataclass
class CreateCalendarEvent:
    _calendar_repository: CalendarRepository

    def __init__(self, calendar_repository: CalendarRepository) -> None:
        self._calendar_repository = calendar_repository

    def execute(self, request: CreateCalendarEventRequest) -> InsertedCalendarEvent:
        event = CalendarEvent(
            name=request.name,
            category=request.category,
            start_datetime=request.start_datetime,
            end_datetime=request.end_datetime,
        )
        return self._calendar_repository.create(event)

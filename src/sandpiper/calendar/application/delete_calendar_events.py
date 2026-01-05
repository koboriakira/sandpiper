from dataclasses import dataclass
from datetime import date

from sandpiper.calendar.domain.calendar_repository import CalendarRepository


@dataclass
class DeleteCalendarEventsRequest:
    target_date: date


@dataclass
class DeleteCalendarEventsResult:
    deleted_count: int


@dataclass
class DeleteCalendarEvents:
    _calendar_repository: CalendarRepository

    def __init__(self, calendar_repository: CalendarRepository) -> None:
        self._calendar_repository = calendar_repository

    def execute(self, request: DeleteCalendarEventsRequest) -> DeleteCalendarEventsResult:
        deleted_count = self._calendar_repository.delete_events_by_date(request.target_date)
        return DeleteCalendarEventsResult(deleted_count=deleted_count)

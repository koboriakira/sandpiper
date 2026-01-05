from abc import ABC, abstractmethod

from sandpiper.calendar.domain.calendar_event import CalendarEvent, InsertedCalendarEvent


class CalendarRepository(ABC):
    @abstractmethod
    def create(self, event: CalendarEvent) -> InsertedCalendarEvent:
        pass

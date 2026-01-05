from abc import ABC, abstractmethod
from datetime import date

from sandpiper.calendar.domain.calendar_event import CalendarEvent, InsertedCalendarEvent


class CalendarRepository(ABC):
    @abstractmethod
    def create(self, event: CalendarEvent) -> InsertedCalendarEvent:
        pass

    @abstractmethod
    def delete_events_by_date(self, target_date: date) -> int:
        """指定された日付のイベントを削除する

        Args:
            target_date: 削除対象の日付

        Returns:
            削除されたイベントの数
        """
        pass

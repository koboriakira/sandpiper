from datetime import date, datetime

from lotion import Lotion

from sandpiper.calendar.domain.calendar_event import CalendarEvent, EventCategory, InsertedCalendarEvent
from sandpiper.calendar.domain.calendar_repository import CalendarRepository
from sandpiper.shared.notion.databases.calendar import (
    CalendarEventCategory,
    CalendarEventName,
    CalendarEventPage,
    CalendarEventStartDate,
)


def _generate_calendar_event_page(event: CalendarEvent) -> CalendarEventPage:
    """CalendarEventからCalendarEventPageを生成する"""
    properties = [
        CalendarEventName.from_plain_text(event.name),
        CalendarEventCategory.from_name(event.category.value),
        CalendarEventStartDate.from_range(start=event.start_datetime, end=event.end_datetime),
    ]
    return CalendarEventPage.create(properties=properties)  # type: ignore[no-any-return]


def _calendar_event_page_to_domain(page: CalendarEventPage) -> CalendarEvent:
    """CalendarEventPageからCalendarEventに変換する"""
    category_prop = page.get_select("カテゴリ")
    start_date_prop = page.get_date("開始日時")
    end_date_prop = page.get_date("終了日時")

    return CalendarEvent(
        name=page.get_title_text(),
        category=EventCategory(category_prop.selected_name) if category_prop.selected_name else EventCategory.PRIVATE,
        start_datetime=start_date_prop.start if start_date_prop.start else datetime.now(),
        end_datetime=end_date_prop.start if end_date_prop.start else datetime.now(),
    )


class NotionCalendarRepository(CalendarRepository):
    def __init__(self) -> None:
        self.client = Lotion.get_instance()

    def create(self, event: CalendarEvent) -> InsertedCalendarEvent:
        notion_event = _generate_calendar_event_page(event)
        page = self.client.create_page(notion_event)
        return InsertedCalendarEvent(
            id=page.id,
            name=event.name,
            category=event.category,
            start_datetime=event.start_datetime,
            end_datetime=event.end_datetime,
        )

    def delete_events_by_date(self, target_date: date) -> int:
        """指定された日付のイベントを削除する

        Args:
            target_date: 削除対象の日付

        Returns:
            削除されたイベントの数
        """
        # データベースから該当する日付のイベントを検索
        pages = self.client.retrieve_pages(CalendarEventPage)
        deleted_count = 0

        # 該当する日付のイベントを削除
        for page in pages:
            event_start_date = datetime.fromisoformat(page.start_date.start) if page.start_date.start else None
            if event_start_date and event_start_date.date() == target_date:
                self.client.remove_page(page.id)
                deleted_count += 1

        return deleted_count

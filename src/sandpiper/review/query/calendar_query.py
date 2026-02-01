from datetime import date, datetime
from typing import Protocol

from lotion import Lotion

from sandpiper.review.query.activity_log_item import ActivityLogItem, ActivityType
from sandpiper.shared.notion.databases.calendar import CalendarEventPage


class CalendarQuery(Protocol):
    def fetch_events_by_date(self, target_date: date) -> list[ActivityLogItem]: ...


class NotionCalendarQuery:
    def __init__(self) -> None:
        self.client = Lotion.get_instance()

    def fetch_events_by_date(self, target_date: date) -> list[ActivityLogItem]:
        """指定された日付のカレンダーイベントを取得する"""
        pages = self.client.retrieve_pages(CalendarEventPage)
        result = []

        for page in pages:
            start_date_str = page.start_date.start if page.start_date.start else None
            end_date_str = page.end_date.start if page.end_date.start else None

            if not start_date_str:
                continue

            start_datetime = datetime.fromisoformat(start_date_str)

            # 指定日付のイベントのみ抽出
            if start_datetime.date() != target_date:
                continue

            # 終了日時がない場合は開始日時と同じにする
            end_datetime = datetime.fromisoformat(end_date_str) if end_date_str else start_datetime

            # カテゴリ取得
            category_prop = page.get_select("カテゴリ")
            category = category_prop.selected_name if category_prop.selected_name else ""

            item = ActivityLogItem(
                activity_type=ActivityType.CALENDAR,
                title=page.get_title_text(),
                start_datetime=start_datetime,
                end_datetime=end_datetime,
                category=category,
            )
            result.append(item)

        return result

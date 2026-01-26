"""カレンダーイベントクエリ

スケジュールタスク作成のためのカレンダーイベント取得クエリ
"""

from dataclasses import dataclass
from datetime import date, datetime
from typing import Protocol

from lotion import Lotion

from sandpiper.calendar.infrastructure.notion_calendar_repository import CalendarEventPage


@dataclass
class CalendarEventDto:
    """カレンダーイベントDTO

    スケジュールタスク作成に必要な情報を保持する
    """

    name: str
    start_datetime: datetime
    end_datetime: datetime

    def calculate_duration_minutes(self) -> int:
        """実行時間を分単位で計算する

        Returns:
            開始時刻から終了時刻までの分数
        """
        duration = self.end_datetime - self.start_datetime
        return int(duration.total_seconds() / 60)

    def get_sort_order(self) -> str:
        """並び順を取得する

        Returns:
            開始時刻をHH:mm形式で返す
        """
        return self.start_datetime.strftime("%H:%M")


class CalendarEventQuery(Protocol):
    """カレンダーイベントクエリのプロトコル"""

    def fetch_events_by_date(self, target_date: date) -> list[CalendarEventDto]: ...


class NotionCalendarEventQuery:
    """Notionカレンダーイベントクエリの実装"""

    def __init__(self) -> None:
        self.client = Lotion.get_instance()

    def fetch_events_by_date(self, target_date: date) -> list[CalendarEventDto]:
        """指定された日付のカレンダーイベントを取得する

        Args:
            target_date: 取得対象の日付

        Returns:
            カレンダーイベントのリスト
        """
        pages = self.client.retrieve_pages(CalendarEventPage)
        result: list[CalendarEventDto] = []

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

            event = CalendarEventDto(
                name=page.get_title_text(),
                start_datetime=start_datetime,
                end_datetime=end_datetime,
            )
            result.append(event)

        # 開始時刻でソート
        result.sort(key=lambda e: e.start_datetime)

        return result

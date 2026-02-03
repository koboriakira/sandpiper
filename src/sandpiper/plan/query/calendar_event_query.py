"""カレンダーイベントクエリ

スケジュールタスク作成のためのカレンダーイベント取得クエリ
"""

from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from typing import Protocol

from lotion import Lotion

from sandpiper.shared.notion.databases.calendar import CalendarEventPage
from sandpiper.shared.valueobject.task_chute_section import TaskChuteSection

# 東京タイムゾーン(UTC+9)
JST = timezone(timedelta(hours=9))


@dataclass
class CalendarEventDto:
    """カレンダーイベントDTO

    スケジュールタスク作成に必要な情報を保持する
    """

    name: str
    start_datetime: datetime
    end_datetime: datetime

    def get_start_datetime_jst(self) -> datetime:
        """開始時刻をJSTで取得する

        Notionから取得した時刻がUTCの場合、9時間追加してJSTに変換する

        Returns:
            JSTの開始時刻
        """
        # タイムゾーン情報がない場合はUTCとして扱い、JSTに変換
        if self.start_datetime.tzinfo is None:
            return self.start_datetime + timedelta(hours=9)
        # タイムゾーン情報がある場合はJSTに変換
        return self.start_datetime.astimezone(JST)

    def get_end_datetime_jst(self) -> datetime:
        """終了時刻をJSTで取得する

        Notionから取得した時刻がUTCの場合、9時間追加してJSTに変換する

        Returns:
            JSTの終了時刻
        """
        # タイムゾーン情報がない場合はUTCとして扱い、JSTに変換
        if self.end_datetime.tzinfo is None:
            return self.end_datetime + timedelta(hours=9)
        # タイムゾーン情報がある場合はJSTに変換
        return self.end_datetime.astimezone(JST)

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
            開始時刻(JST)をHH:mm形式で返す
        """
        return self.get_start_datetime_jst().strftime("%H:%M")

    def get_section(self) -> TaskChuteSection:
        """開始時刻(JST)からセクションを判定する

        Returns:
            該当するTaskChuteSection
        """
        return TaskChuteSection.new(self.get_start_datetime_jst())


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
            start_date_str = page.date_range.start if page.date_range.start else None
            end_date_str = page.date_range.end if page.date_range.end else None

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

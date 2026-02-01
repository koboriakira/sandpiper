from lotion import BasePage, notion_database, notion_prop
from lotion.properties import Date, Select, Title

DATABASE_ID = "2dd6567a3bbf80219a93f941334bd556"


@notion_prop("名前")
class CalendarEventName(Title):  # type: ignore[misc]
    ...


@notion_prop("カテゴリ")
class CalendarEventCategory(Select):  # type: ignore[misc]
    ...


@notion_prop("開始日時")
class CalendarEventStartDate(Date):  # type: ignore[misc]
    ...


@notion_prop("終了日時")
class CalendarEventEndDate(Date):  # type: ignore[misc]
    ...


@notion_database(DATABASE_ID)
class CalendarEventPage(BasePage):  # type: ignore[misc]
    """カレンダーイベントのNotionページ

    ドメイン変換ロジック(to_domain, generate)はcalendar.infrastructureで実装
    """

    name: CalendarEventName
    category: CalendarEventCategory
    start_date: CalendarEventStartDate
    end_date: CalendarEventEndDate

from lotion import notion_prop  # type: ignore[import-untyped]
from lotion.properties import Date, Select, Title  # type: ignore[import-untyped]

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

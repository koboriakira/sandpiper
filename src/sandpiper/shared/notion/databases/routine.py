from lotion import notion_prop  # type: ignore[import-untyped]
from lotion.properties import Date, MultiSelect, Number, Text  # type: ignore[import-untyped]

DATABASE_ID = "d21db86c92034ff498999d62354e8fe1"


@notion_prop("次回実行日")
class RoutineNextDate(Date):  # type: ignore[misc]
    ...


@notion_prop("実行時間")
class RoutineExecutionTime(Number):  # type: ignore[misc]
    ...


@notion_prop("コンテクスト")
class RoutineContext(MultiSelect):  # type: ignore[misc]
    ...


@notion_prop("並び順")
class RoutineSortOrder(Text):  # type: ignore[misc]
    ...

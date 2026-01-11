from lotion import notion_prop  # type: ignore[import-untyped]
from lotion.properties import Date, Number  # type: ignore[import-untyped]

DATABASE_ID = "d21db86c92034ff498999d62354e8fe1"


@notion_prop("次回実行日")
class RoutineNextDate(Date):  # type: ignore[misc]
    ...


@notion_prop("実行時間")
class RoutineExecutionTime(Number):  # type: ignore[misc]
    ...

from lotion import notion_prop
from lotion.properties import Date, MultiSelect, Number, Text

DATABASE_ID = "d21db86c92034ff498999d62354e8fe1"


@notion_prop("次回実行日")
class RoutineNextDate(Date): ...


@notion_prop("実行時間")
class RoutineExecutionTime(Number): ...


@notion_prop("コンテクスト")
class RoutineContext(MultiSelect): ...


@notion_prop("並び順")
class RoutineSortOrder(Text): ...


@notion_prop("予定")
class RoutineScheduledDate(Date): ...

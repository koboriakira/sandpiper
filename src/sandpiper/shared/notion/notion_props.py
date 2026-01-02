from lotion import notion_prop
from lotion.properties import Date, Select, Status, Title


@notion_prop("名前")
class TodoName(Title): ...


@notion_prop("ステータス")
class TodoStatus(Status): ...


@notion_prop("セクション")
class TodoSection(Select): ...


@notion_prop("実施期間")
class TodoLogDate(Date): ...


@notion_prop("タスク種別")
class TodoKind(Select): ...

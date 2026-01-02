from lotion import notion_prop
from lotion.properties import Date, Relation, Select, Status, Title

# ToDo関連のプロパティ


@notion_prop("名前")
class TodoName(Title): ...


@notion_prop("ステータス")
class TodoStatus(Status): ...


@notion_prop("セクション")
class TodoSection(Select): ...


@notion_prop("実施期間")
class TodoLogDate(Date): ...


@notion_prop("タスク種別")
class TodoKindProp(Select): ...


@notion_prop("プロジェクト")
class TodoProjectProp(Relation): ...


@notion_prop("プロジェクトタスク")
class TodoProjectTaskProp(Relation): ...


# ルーティン関連のプロパティ
@notion_prop("次回実行日")
class RoutineNextDate(Date): ...

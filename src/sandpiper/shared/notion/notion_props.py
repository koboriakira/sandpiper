from lotion import notion_prop  # type: ignore[import-untyped]
from lotion.properties import Date, Relation, Select, Status, Title  # type: ignore[import-untyped]

# ToDo関連のプロパティ


@notion_prop("名前")
class TodoName(Title):  # type: ignore[misc]
    ...


@notion_prop("ステータス")
class TodoStatus(Status):  # type: ignore[misc]
    ...


@notion_prop("セクション")
class TodoSection(Select):  # type: ignore[misc]
    ...


@notion_prop("実施期間")
class TodoLogDate(Date):  # type: ignore[misc]
    ...


@notion_prop("タスク種別")
class TodoKindProp(Select):  # type: ignore[misc]
    ...


@notion_prop("プロジェクト")
class TodoProjectProp(Relation):  # type: ignore[misc]
    ...


@notion_prop("プロジェクトタスク")
class TodoProjectTaskProp(Relation):  # type: ignore[misc]
    ...


# ルーティン関連のプロパティ
@notion_prop("次回実行日")
class RoutineNextDate(Date):  # type: ignore[misc]
    ...

from lotion import notion_prop  # type: ignore[import-untyped]
from lotion.properties import (  # type: ignore[import-untyped]
    Checkbox,
    Date,
    Number,
    Relation,
    Select,
    Status,
    Title,
)

DATABASE_ID = "2db6567a3bbf805ba379f942cdf0e264"


@notion_prop("名前")
class TodoName(Title):  # type: ignore[misc]
    ...


@notion_prop("ステータス")
class TodoStatus(Status):  # type: ignore[misc]
    ...


@notion_prop("セクション")
class TodoSection(Select):  # type: ignore[misc]
    ...


@notion_prop("今日中にやる")
class TodoIsTodayProp(Checkbox):  # type: ignore[misc]
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


@notion_prop("実行時間")
class TodoExecutionTime(Number):  # type: ignore[misc]
    ...


@notion_prop("論理削除")
class TodoIsDeleted(Checkbox):  # type: ignore[misc]
    ...

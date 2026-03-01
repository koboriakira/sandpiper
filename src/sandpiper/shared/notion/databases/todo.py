from lotion import notion_prop
from lotion.properties import (
    Checkbox,
    Date,
    MultiSelect,
    Number,
    Relation,
    Select,
    Status,
    Text,
    Title,
    Url,
)

DATABASE_ID = "2db6567a3bbf805ba379f942cdf0e264"


@notion_prop("名前")
class TodoName(Title): ...


@notion_prop("ステータス")
class TodoStatus(Status): ...


@notion_prop("セクション")
class TodoSection(Select): ...


@notion_prop("今日中にやる")
class TodoIsTodayProp(Checkbox): ...


@notion_prop("実施期間")
class TodoLogDate(Date): ...


@notion_prop("タスク種別")
class TodoKindProp(Select): ...


@notion_prop("プロジェクト")
class TodoProjectProp(Relation): ...


@notion_prop("プロジェクトタスク")
class TodoProjectTaskProp(Relation): ...


@notion_prop("実行時間")
class TodoExecutionTime(Number): ...


@notion_prop("論理削除")
class TodoIsDeleted(Checkbox): ...


@notion_prop("コンテクスト")
class TodoContext(MultiSelect): ...


@notion_prop("並び順")
class TodoSortOrder(Text): ...


@notion_prop("予定")
class TodoScheduledDate(Date): ...


@notion_prop("Claude")
class TodoClaudeUrl(Url): ...

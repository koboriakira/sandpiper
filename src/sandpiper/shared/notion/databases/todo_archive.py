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

DATABASE_ID = "c776567a3bbf8334b2e3810812854fb3"


@notion_prop("名前")
class TodoArchiveName(Title): ...


@notion_prop("ステータス")
class TodoArchiveStatus(Status): ...


@notion_prop("セクション")
class TodoArchiveSection(Select): ...


@notion_prop("今日中にやる")
class TodoArchiveIsTodayProp(Checkbox): ...


@notion_prop("実施期間")
class TodoArchiveLogDate(Date): ...


@notion_prop("タスク種別")
class TodoArchiveKindProp(Select): ...


@notion_prop("プロジェクト")
class TodoArchiveProjectProp(Relation): ...


@notion_prop("プロジェクトタスク")
class TodoArchiveProjectTaskProp(Relation): ...


@notion_prop("実行時間")
class TodoArchiveExecutionTime(Number): ...


@notion_prop("論理削除")
class TodoArchiveIsDeleted(Checkbox): ...


@notion_prop("コンテクスト")
class TodoArchiveContext(MultiSelect): ...


@notion_prop("並び順")
class TodoArchiveSortOrder(Text): ...


@notion_prop("Claude")
class TodoArchiveClaudeUrl(Url): ...

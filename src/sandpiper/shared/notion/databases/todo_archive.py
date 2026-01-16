from lotion import notion_prop  # type: ignore[import-untyped]
from lotion.properties import (  # type: ignore[import-untyped]
    Checkbox,
    Date,
    MultiSelect,
    Number,
    Relation,
    Select,
    Status,
    Text,
    Title,
)

DATABASE_ID = "c776567a3bbf8334b2e3810812854fb3"


@notion_prop("名前")
class TodoArchiveName(Title):  # type: ignore[misc]
    ...


@notion_prop("ステータス")
class TodoArchiveStatus(Status):  # type: ignore[misc]
    ...


@notion_prop("セクション")
class TodoArchiveSection(Select):  # type: ignore[misc]
    ...


@notion_prop("今日中にやる")
class TodoArchiveIsTodayProp(Checkbox):  # type: ignore[misc]
    ...


@notion_prop("実施期間")
class TodoArchiveLogDate(Date):  # type: ignore[misc]
    ...


@notion_prop("タスク種別")
class TodoArchiveKindProp(Select):  # type: ignore[misc]
    ...


@notion_prop("プロジェクト")
class TodoArchiveProjectProp(Relation):  # type: ignore[misc]
    ...


@notion_prop("プロジェクトタスク")
class TodoArchiveProjectTaskProp(Relation):  # type: ignore[misc]
    ...


@notion_prop("実行時間")
class TodoArchiveExecutionTime(Number):  # type: ignore[misc]
    ...


@notion_prop("論理削除")
class TodoArchiveIsDeleted(Checkbox):  # type: ignore[misc]
    ...


@notion_prop("コンテクスト")
class TodoArchiveContext(MultiSelect):  # type: ignore[misc]
    ...


@notion_prop("並び順")
class TodoArchiveSortOrder(Text):  # type: ignore[misc]
    ...

from lotion import notion_prop
from lotion.properties import Checkbox, Date, MultiSelect, Relation, Status, Text, Title

DATABASE_ID = "2db6567a3bbf80078961d42908b5dd49"


@notion_prop("名前")
class ProjectTaskName(Title): ...


@notion_prop("ステータス")
class ProjectTaskStatus(Status): ...


@notion_prop("プロジェクト")
class ProjectTaskProjectProp(Relation): ...


@notion_prop("コンテクスト")
class ProjectTaskContext(MultiSelect): ...


@notion_prop("論理削除")
class ProjectTaskIsDeleted(Checkbox): ...


@notion_prop("並び順")
class ProjectTaskSortOrder(Text): ...


@notion_prop("予定")
class ProjectTaskScheduledDate(Date): ...

from lotion import notion_prop  # type: ignore[import-untyped]
from lotion.properties import Checkbox, MultiSelect, Relation, Status, Text, Title  # type: ignore[import-untyped]

DATABASE_ID = "2db6567a3bbf80078961d42908b5dd49"


@notion_prop("名前")
class ProjectTaskName(Title):  # type: ignore[misc]
    ...


@notion_prop("ステータス")
class ProjectTaskStatus(Status):  # type: ignore[misc]
    ...


@notion_prop("プロジェクト")
class ProjectTaskProjectProp(Relation):  # type: ignore[misc]
    ...


@notion_prop("コンテクスト")
class ProjectTaskContext(MultiSelect):  # type: ignore[misc]
    ...


@notion_prop("論理削除")
class ProjectTaskIsDeleted(Checkbox):  # type: ignore[misc]
    ...


@notion_prop("並び順")
class ProjectTaskSortOrder(Text):  # type: ignore[misc]
    ...

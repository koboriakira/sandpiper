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


# カレンダー関連のプロパティ
@notion_prop("名前")
class CalendarEventName(Title):  # type: ignore[misc]
    ...


@notion_prop("カテゴリ")
class CalendarEventCategory(Select):  # type: ignore[misc]
    ...


@notion_prop("開始日時")
class CalendarEventStartDate(Date):  # type: ignore[misc]
    ...


@notion_prop("終了日時")
class CalendarEventEndDate(Date):  # type: ignore[misc]
    ...


# プロジェクト関連のプロパティ
@notion_prop("名前")
class ProjectName(Title):  # type: ignore[misc]
    ...


@notion_prop("開始日")
class ProjectStartDate(Date):  # type: ignore[misc]
    ...


@notion_prop("終了日")
class ProjectEndDate(Date):  # type: ignore[misc]
    ...


# プロジェクトタスク関連のプロパティ
@notion_prop("名前")
class ProjectTaskName(Title):  # type: ignore[misc]
    ...


@notion_prop("ステータス")
class ProjectTaskStatus(Status):  # type: ignore[misc]
    ...


@notion_prop("プロジェクト")
class ProjectTaskProjectProp(Relation):  # type: ignore[misc]
    ...


# レシピ関連のプロパティ
@notion_prop("名前")
class RecipeName(Title):  # type: ignore[misc]
    ...


@notion_prop("材料")
class RecipeIngredientsProp(Relation):  # type: ignore[misc]
    ...


@notion_prop("Reference")
class RecipeReferenceProp:  # type: ignore[misc]
    ...


# 買い物関連のプロパティ
@notion_prop("名前")
class ShoppingName(Title):  # type: ignore[misc]
    ...

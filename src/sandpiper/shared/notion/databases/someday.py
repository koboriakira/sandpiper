from lotion import notion_prop  # type: ignore[import-untyped]
from lotion.properties import Checkbox, MultiSelect, Select, Title  # type: ignore[import-untyped]

DATABASE_ID = "2db6567a3bbf80a8b3f3e3560cfe380f"


@notion_prop("名前")
class SomedayName(Title):  # type: ignore[misc]
    ...


@notion_prop("タイミング")
class SomedayTiming(Select):  # type: ignore[misc]
    ...


@notion_prop("明日やる")
class SomedayDoTomorrow(Checkbox):  # type: ignore[misc]
    ...


@notion_prop("論理削除")
class SomedayIsDeleted(Checkbox):  # type: ignore[misc]
    ...


@notion_prop("コンテクスト")
class SomedayContext(MultiSelect):  # type: ignore[misc]
    ...

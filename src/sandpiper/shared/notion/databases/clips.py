from lotion import notion_prop  # type: ignore[import-untyped]
from lotion.properties import Checkbox, Select, Title, Url  # type: ignore[import-untyped]

DATABASE_ID = "2e66567a3bbf80aa8c83f113aa101d44"  # TODO: 実際のNotion Clips Database IDに置き換えてください


@notion_prop("名前")
class ClipsName(Title):  # type: ignore[misc]
    ...


@notion_prop("URL")
class ClipsUrl(Url):  # type: ignore[misc]
    ...


@notion_prop("種類")
class ClipsTypeProp(Select):  # type: ignore[misc]
    ...


@notion_prop("タイトル自動取得")
class ClipsAutoFetchTitle(Checkbox):  # type: ignore[misc]
    ...

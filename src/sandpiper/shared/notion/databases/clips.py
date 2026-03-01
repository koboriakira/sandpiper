from lotion import notion_prop
from lotion.properties import Checkbox, Select, Title, Url

DATABASE_ID = "2e66567a3bbf80aa8c83f113aa101d44"  # TODO: 実際のNotion Clips Database IDに置き換えてください


@notion_prop("名前")
class ClipsName(Title): ...


@notion_prop("URL")
class ClipsUrl(Url): ...


@notion_prop("種類")
class ClipsTypeProp(Select): ...


@notion_prop("タイトル自動取得")
class ClipsAutoFetchTitle(Checkbox): ...


@notion_prop("未処理")
class ClipsUnprocessed(Checkbox): ...

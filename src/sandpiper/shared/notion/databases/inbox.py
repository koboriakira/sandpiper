from lotion import notion_prop  # type: ignore[import-untyped]
from lotion.properties import Select, Title, Url  # type: ignore[import-untyped]

DATABASE_ID = "2e66567a3bbf80aa8c83f113aa101d44"


@notion_prop("名前")
class InboxName(Title):  # type: ignore[misc]
    ...


@notion_prop("URL")
class InboxUrl(Url):  # type: ignore[misc]
    ...


@notion_prop("種類")
class InboxType(Select):  # type: ignore[misc]
    ...

from lotion import notion_prop  # type: ignore[import-untyped]
from lotion.properties import Title, Url  # type: ignore[import-untyped]

DATABASE_ID = "YOUR_CLIPS_DATABASE_ID"  # TODO: 実際のNotion Clips Database IDに置き換えてください


@notion_prop("名前")
class ClipsName(Title):  # type: ignore[misc]
    ...


@notion_prop("URL")
class ClipsUrl(Url):  # type: ignore[misc]
    ...

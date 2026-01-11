from lotion import notion_prop  # type: ignore[import-untyped]
from lotion.properties import Title  # type: ignore[import-untyped]

DATABASE_ID = "b917fd7e2fe54030879f9eea5e8827bb"


@notion_prop("名前")
class ShoppingName(Title):  # type: ignore[misc]
    ...

from lotion import notion_prop
from lotion.properties import Title

DATABASE_ID = "b917fd7e2fe54030879f9eea5e8827bb"


@notion_prop("名前")
class ShoppingName(Title):  # type: ignore[misc]
    ...

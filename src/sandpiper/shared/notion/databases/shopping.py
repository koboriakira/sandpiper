from lotion import notion_prop
from lotion.properties import Checkbox, Status, Title

DATABASE_ID = "b917fd7e2fe54030879f9eea5e8827bb"

PURCHASED_STATUS = "購入済"


@notion_prop("名前")
class ShoppingName(Title): ...


@notion_prop("買う")
class ShoppingWant(Checkbox): ...


@notion_prop("購入済")
class ShoppingPurchased(Status): ...

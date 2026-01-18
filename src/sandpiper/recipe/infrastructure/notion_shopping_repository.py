from lotion import BasePage, Lotion, notion_database

from sandpiper.shared.notion.databases import shopping as shopping_db
from sandpiper.shared.notion.databases.shopping import ShoppingName


@notion_database(shopping_db.DATABASE_ID)
class ShoppingPage(BasePage):  # type: ignore[misc]
    name: ShoppingName

    @staticmethod
    def generate(name: str) -> "ShoppingPage":
        properties = [
            ShoppingName.from_plain_text(name),
        ]
        return ShoppingPage.create(properties=properties)  # type: ignore[no-any-return]


class NotionShoppingRepository:
    def __init__(self) -> None:
        self.client = Lotion.get_instance()

    def find_or_create(self, name: str) -> str:
        """買い物アイテムを名前で検索し、存在しなければ作成する。ページIDを返す。"""
        existing_pages = self.client.search_pages(
            cls=ShoppingPage,
            props=[ShoppingName.from_plain_text(name)],
        )
        if existing_pages:
            return existing_pages[0].id  # type: ignore[no-any-return]

        shopping_page = ShoppingPage.generate(name)
        page = self.client.create_page(shopping_page)
        return page.id  # type: ignore[no-any-return]

from lotion import BasePage, Lotion, notion_database
from lotion.filter import Builder

from sandpiper.shared.notion.databases import shopping as shopping_db
from sandpiper.shared.notion.databases.shopping import PURCHASED_STATUS, ShoppingName, ShoppingPurchased, ShoppingWant


@notion_database(shopping_db.DATABASE_ID)
class ShoppingPage(BasePage):  # type: ignore[misc]
    name: ShoppingName
    want: ShoppingWant | None = None
    purchased: ShoppingPurchased | None = None

    @staticmethod
    def generate(name: str) -> "ShoppingPage":
        properties = [
            ShoppingName.from_plain_text(name),
            ShoppingWant.true(),
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

    def list_want(self) -> list[str]:
        """「買う」チェックボックスがONのアイテム名一覧を返す。"""
        filter_param = (
            Builder.create()
            .add_filter_param({"property": ShoppingWant.PROP_NAME, "checkbox": {"equals": True}})
            .build()
        )
        pages: list[ShoppingPage] = self.client.retrieve_database(
            database_id=shopping_db.DATABASE_ID, filter_param=filter_param, cls=ShoppingPage
        )
        return [page.get_title_text() for page in pages]

    def buy(self, name: str) -> str | None:
        """買い物アイテムを名前で検索し、「購入済」ステータスに変更する。見つからない場合はNoneを返す。"""
        existing_pages = self.client.search_pages(
            cls=ShoppingPage,
            props=[ShoppingName.from_plain_text(name)],
        )
        if not existing_pages:
            return None
        page = existing_pages[0]
        page.set_prop(ShoppingPurchased.from_status_name(PURCHASED_STATUS))
        self.client.update(page)
        return page.id  # type: ignore[no-any-return]

    def want(self, name: str) -> str:
        """買い物アイテムを名前で検索し、存在しなければ作成して「買う」チェックボックスをONにする。ページIDを返す。"""
        existing_pages = self.client.search_pages(
            cls=ShoppingPage,
            props=[ShoppingName.from_plain_text(name)],
        )
        if existing_pages:
            page = existing_pages[0]
            page.set_prop(ShoppingWant.true())
            self.client.update(page)
            return page.id  # type: ignore[no-any-return]

        shopping_page = ShoppingPage.generate(name)
        created = self.client.create_page(shopping_page)
        return created.id  # type: ignore[no-any-return]

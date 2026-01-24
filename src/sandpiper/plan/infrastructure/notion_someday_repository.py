from lotion import Lotion

from sandpiper.plan.domain.someday_item import SomedayItem
from sandpiper.plan.domain.someday_repository import SomedayRepository
from sandpiper.shared.notion.databases.someday import SomedayPage


class NotionSomedayRepository(SomedayRepository):
    """Notionを使用したサムデイリストリポジトリ"""

    def __init__(self) -> None:
        self._client = Lotion.get_instance()

    def fetch_all(self, include_deleted: bool = False) -> list[SomedayItem]:
        """全てのサムデイアイテムを取得"""
        pages = SomedayPage.fetch_all(self._client)
        result = []
        for page in pages:
            item = page.to_domain()
            if not include_deleted and item.is_deleted:
                continue
            result.append(item)
        return result

    def fetch_tomorrow_items(self) -> list[SomedayItem]:
        """「明日やる」フラグが立っているアイテムを取得"""
        all_items = self.fetch_all(include_deleted=False)
        return [item for item in all_items if item.do_tomorrow]

    def save(self, item: SomedayItem) -> SomedayItem:
        """サムデイアイテムを保存"""
        someday_page = SomedayPage.generate(item)
        created_page: SomedayPage = self._client.create_page(someday_page)
        return created_page.to_domain()

    def update(self, item: SomedayItem) -> None:
        """サムデイアイテムを更新"""
        updated_page = SomedayPage.generate(item)
        self._client.update(updated_page)

    def delete(self, item_id: str) -> None:
        """サムデイアイテムを削除"""
        self._client.remove_page(item_id)


if __name__ == "__main__":
    # uv run python -m sandpiper.plan.infrastructure.notion_someday_repository
    repo = NotionSomedayRepository()
    items = repo.fetch_all()
    for item in items:
        print(item)

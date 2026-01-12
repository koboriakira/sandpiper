from lotion import Lotion  # type: ignore[import-untyped]

from sandpiper.plan.domain.someday_item import SomedayItem, SomedayTiming
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
        page = self._client.retrieve_page(item.id, cls=SomedayPage)
        updated_page = SomedayPage.generate(item)
        updated_page.id = page.id
        self._client.update(updated_page)

    def delete(self, item_id: str) -> None:
        """サムデイアイテムを論理削除"""
        page: SomedayPage = self._client.retrieve_page(item_id, cls=SomedayPage)
        item = page.to_domain()
        item.is_deleted = True
        updated_page = SomedayPage.generate(item)
        updated_page.id = page.id
        self._client.update(updated_page)

    def fetch_by_timing_and_context(self, timing: SomedayTiming, context: str) -> list[SomedayItem]:
        """タイミングとコンテクストでフィルタリングしたアイテムを取得"""
        all_items = self.fetch_all(include_deleted=False)
        return [item for item in all_items if item.timing == timing and context in item.context]

    def _parse_timing(self, timing_name: str) -> SomedayTiming:
        """タイミング名からEnumに変換"""
        timing_map = {
            "明日": SomedayTiming.TOMORROW,
            "いつか": SomedayTiming.SOMEDAY,
            "ついでに": SomedayTiming.INCIDENTALLY,
        }
        return timing_map.get(timing_name, SomedayTiming.SOMEDAY)


if __name__ == "__main__":
    # uv run python -m sandpiper.plan.infrastructure.notion_someday_repository
    repo = NotionSomedayRepository()
    items = repo.fetch_all()
    for item in items:
        print(item)

from lotion import Lotion  # type: ignore[import-untyped]

from sandpiper.plan.domain.someday_item import SomedayItem, SomedayTiming
from sandpiper.plan.domain.someday_repository import SomedayRepository
from sandpiper.shared.notion.databases import someday as someday_db
from sandpiper.shared.notion.databases.someday import (
    SomedayContext,
    SomedayDoTomorrow,
    SomedayIsDeleted,
    SomedayName,
)
from sandpiper.shared.notion.databases.someday import (
    SomedayTiming as SomedayTimingProp,
)


class NotionSomedayRepository(SomedayRepository):
    """Notionを使用したサムデイリストリポジトリ"""

    def __init__(self) -> None:
        self.client = Lotion.get_instance()

    def fetch_all(self, include_deleted: bool = False) -> list[SomedayItem]:
        """全てのサムデイアイテムを取得"""
        items = self.client.retrieve_database(someday_db.DATABASE_ID)
        result = []
        for item in items:
            is_deleted = item.get_checkbox("論理削除").checked
            if not include_deleted and is_deleted:
                continue

            timing_name = item.get_select("タイミング").selected_name
            timing = SomedayTiming.TOMORROW if timing_name == "明日" else SomedayTiming.SOMEDAY
            do_tomorrow = item.get_checkbox("明日やる").checked
            context_prop = item.get_multi_select("コンテクスト")
            context = [v.name for v in context_prop.values] if context_prop else []

            someday_item = SomedayItem(
                id=item.id,
                title=item.get_title_text(),
                timing=timing,
                do_tomorrow=do_tomorrow,
                is_deleted=is_deleted,
                context=context,
            )
            result.append(someday_item)
        return result

    def fetch_tomorrow_items(self) -> list[SomedayItem]:
        """「明日やる」フラグが立っているアイテムを取得"""
        all_items = self.fetch_all(include_deleted=False)
        return [item for item in all_items if item.do_tomorrow]

    def save(self, item: SomedayItem) -> SomedayItem:
        """サムデイアイテムを保存"""
        page = self.client.create_page_in_database(someday_db.DATABASE_ID)
        page.set_prop(SomedayName.from_plain_text(item.title))
        page.set_prop(SomedayTimingProp.from_name(item.timing.value))
        page.set_prop(SomedayDoTomorrow.true() if item.do_tomorrow else SomedayDoTomorrow.false())
        page.set_prop(SomedayIsDeleted.false())
        if item.context:
            page.set_prop(SomedayContext.from_name(item.context))
        created_page = self.client.update(page)
        return SomedayItem(
            id=created_page.id,
            title=item.title,
            timing=item.timing,
            do_tomorrow=item.do_tomorrow,
            is_deleted=False,
            context=item.context,
        )

    def update(self, item: SomedayItem) -> None:
        """サムデイアイテムを更新"""
        page = self.client.retrieve_page(item.id)
        page.set_prop(SomedayName.from_plain_text(item.title))
        page.set_prop(SomedayTimingProp.from_name(item.timing.value))
        page.set_prop(SomedayDoTomorrow.true() if item.do_tomorrow else SomedayDoTomorrow.false())
        page.set_prop(SomedayIsDeleted.true() if item.is_deleted else SomedayIsDeleted.false())
        if item.context:
            page.set_prop(SomedayContext.from_name(item.context))
        self.client.update(page)

    def delete(self, item_id: str) -> None:
        """サムデイアイテムを論理削除"""
        page = self.client.retrieve_page(item_id)
        page.set_prop(SomedayIsDeleted.true())
        self.client.update(page)


if __name__ == "__main__":
    # uv run python -m sandpiper.plan.infrastructure.notion_someday_repository
    repo = NotionSomedayRepository()
    items = repo.fetch_all()
    for item in items:
        print(item)

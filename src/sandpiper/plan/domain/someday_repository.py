from typing import Protocol

from sandpiper.plan.domain.someday_item import SomedayItem


class SomedayRepository(Protocol):
    """サムデイリストリポジトリのインターフェース"""

    def fetch_all(self, include_deleted: bool = False) -> list[SomedayItem]:
        """全てのサムデイアイテムを取得"""
        ...

    def fetch_tomorrow_items(self) -> list[SomedayItem]:
        """「明日やる」フラグが立っているアイテムを取得"""
        ...

    def save(self, item: SomedayItem) -> SomedayItem:
        """サムデイアイテムを保存"""
        ...

    def update(self, item: SomedayItem) -> None:
        """サムデイアイテムを更新"""
        ...

    def delete(self, item_id: str) -> None:
        """サムデイアイテムを論理削除"""
        ...

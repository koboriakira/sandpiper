from typing import Protocol


class ShoppingRepository(Protocol):
    def find_or_create(self, name: str) -> str:
        """買い物アイテムを名前で検索し、存在しなければ作成する。ページIDを返す。"""
        ...

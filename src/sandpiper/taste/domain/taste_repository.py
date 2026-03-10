from typing import Protocol

from sandpiper.taste.domain.taste_item import InsertedTasteItem, TasteItem


class TasteRepository(Protocol):
    def save(self, item: TasteItem) -> InsertedTasteItem: ...

    def fetch_all(self) -> list[InsertedTasteItem]: ...

from sandpiper.taste.domain.taste_item import InsertedTasteItem
from sandpiper.taste.domain.taste_repository import TasteRepository


class ListTaste:
    def __init__(self, repository: TasteRepository) -> None:
        self._repository = repository

    def execute(self) -> list[InsertedTasteItem]:
        return self._repository.fetch_all()

from sandpiper.taste.domain.taste_item import InsertedTasteItem, TasteItem
from sandpiper.taste.domain.taste_repository import TasteRepository


class AddTaste:
    def __init__(self, repository: TasteRepository) -> None:
        self._repository = repository

    def execute(
        self,
        title: str,
        tags: list[str] | None = None,
        comment: str | None = None,
        place_page_id: str | None = None,
        impression: str | None = None,
    ) -> InsertedTasteItem:
        item = TasteItem(
            title=title,
            tags=tags or [],
            comment=comment,
            place_page_id=place_page_id,
            impression=impression,
        )
        return self._repository.save(item)

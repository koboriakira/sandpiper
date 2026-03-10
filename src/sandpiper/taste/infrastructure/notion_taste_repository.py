from lotion import BasePage, Lotion, notion_database

from sandpiper.shared.notion.databases import taste as taste_db
from sandpiper.shared.notion.databases.taste import (
    TasteComment,
    TasteImpression,
    TasteName,
    TastePlace,
    TasteTags,
)
from sandpiper.taste.domain.taste_item import InsertedTasteItem, TasteItem


@notion_database(taste_db.DATABASE_ID)
class TastePage(BasePage):  # type: ignore[misc]
    name: TasteName
    tags: TasteTags | None = None
    comment: TasteComment | None = None
    place: TastePlace | None = None
    impression: TasteImpression | None = None

    @staticmethod
    def generate(item: TasteItem) -> "TastePage":
        properties = [TasteName.from_plain_text(item.title)]
        if item.tags:
            properties.append(TasteTags.from_name_list(item.tags))
        if item.comment:
            properties.append(TasteComment.from_plain_text(item.comment))
        if item.place_page_id:
            properties.append(TastePlace.from_id(item.place_page_id))
        if item.impression:
            properties.append(TasteImpression.from_name(item.impression))
        return TastePage.create(properties=properties)

    def to_domain(self) -> InsertedTasteItem:
        tags_prop = self.get_multi_select("Tags")
        tags = [v.name for v in tags_prop.values] if tags_prop and tags_prop.values else []
        comment_prop = self.get_plain_text("一言コメント")
        place_ids = self.get_relation("場所").id_list
        impression_prop = self.get_select("感想")
        return InsertedTasteItem(
            id=self.id,
            title=self.get_title_text(),
            tags=tags,
            comment=comment_prop if comment_prop else None,
            place_page_id=place_ids[0] if place_ids else None,
            impression=impression_prop.selected_name if impression_prop else None,
        )


class NotionTasteRepository:
    def __init__(self) -> None:
        self._client = Lotion.get_instance()

    def save(self, item: TasteItem) -> InsertedTasteItem:
        page = TastePage.generate(item)
        created = self._client.create_page(page)
        result = self._client.retrieve_page(created.id, TastePage)
        return result.to_domain()  # type: ignore[no-any-return]

    def fetch_all(self) -> list[InsertedTasteItem]:
        pages: list[TastePage] = self._client.retrieve_database(taste_db.DATABASE_ID, cls=TastePage)
        return [page.to_domain() for page in pages]  # type: ignore[return-value]

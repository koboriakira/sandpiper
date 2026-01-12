from lotion import BasePage, Lotion, notion_database  # type: ignore[import-untyped]

from sandpiper.clips.domain.clip import Clip, InsertedClip
from sandpiper.clips.domain.clips_repository import ClipsRepository
from sandpiper.shared.notion.databases import clips as clips_db
from sandpiper.shared.notion.databases.clips import ClipsName, ClipsUrl


@notion_database(clips_db.DATABASE_ID)
class ClipsPage(BasePage):  # type: ignore[misc]
    name: ClipsName
    url: ClipsUrl | None = None

    @staticmethod
    def generate(clip: Clip) -> "ClipsPage":
        properties = [
            ClipsName.from_plain_text(clip.title),
            ClipsUrl.from_url(clip.url),
        ]
        return ClipsPage.create(properties=properties)  # type: ignore[no-any-return]


class NotionClipsRepository(ClipsRepository):
    def __init__(self) -> None:
        self._client = Lotion.get_instance()

    def save(self, clip: Clip) -> InsertedClip:
        clips_page = ClipsPage.generate(clip)
        page = self._client.create_page(clips_page)
        return InsertedClip(
            id=page.id,
            title=clip.title,
            url=clip.url,
        )

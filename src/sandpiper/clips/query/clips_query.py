from typing import Protocol

from lotion import Lotion

from sandpiper.clips.infrastructure.notion_clips_repository import ClipsPage
from sandpiper.clips.query.unprocessed_clip_item import UnprocessedClipItem
from sandpiper.shared.notion.databases import clips as clips_db


class ClipsQuery(Protocol):
    def fetch_unprocessed(self) -> list[UnprocessedClipItem]: ...


class NotionClipsQuery:
    def __init__(self) -> None:
        self._client = Lotion.get_instance()

    def fetch_unprocessed(self) -> list[UnprocessedClipItem]:
        """未処理(unprocessed=True)のClipsを取得する"""
        filter_param = {
            "property": "未処理",
            "checkbox": {
                "equals": True,
            },
        }
        pages: list[ClipsPage] = self._client.retrieve_database(
            clips_db.DATABASE_ID,
            filter_param=filter_param,
            cls=ClipsPage,
        )
        return [
            UnprocessedClipItem(
                title=page.get_title_text(),
                url=page.url.url if page.url else "",
            )
            for page in pages
        ]

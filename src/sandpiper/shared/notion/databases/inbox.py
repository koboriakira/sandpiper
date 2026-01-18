from enum import Enum

from lotion import notion_prop
from lotion.properties import Select, Title, Url


class InboxType(Enum):
    """Inboxの種類を表すEnum。"""

    WEB = "Web"
    VIDEO = "動画"
    MUSIC = "音楽"
    OTHER = "その他"

    @classmethod
    def from_url(cls, url: str) -> "InboxType":
        """URLからInboxTypeを判別する。"""
        if "youtube.com" in url or "youtu.be" in url:
            return cls.VIDEO
        return cls.WEB


DATABASE_ID = "2e66567a3bbf80aa8c83f113aa101d44"


@notion_prop("名前")
class InboxName(Title):  # type: ignore[misc]
    ...


@notion_prop("URL")
class InboxUrl(Url):  # type: ignore[misc]
    ...


@notion_prop("種類")
class InboxTypeProp(Select):  # type: ignore[misc]
    ...

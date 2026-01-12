from dataclasses import dataclass

from sandpiper.shared.notion.databases.inbox import InboxType


@dataclass(frozen=True)
class Clip:
    """Clip entity representing a web clip."""

    title: str
    url: str
    inbox_type: InboxType


@dataclass(frozen=True)
class InsertedClip:
    """Inserted clip with Notion page ID."""

    id: str
    title: str
    url: str
    inbox_type: InboxType

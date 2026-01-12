from dataclasses import dataclass


@dataclass(frozen=True)
class Clip:
    """Clip entity representing a web clip."""

    title: str
    url: str


@dataclass(frozen=True)
class InsertedClip:
    """Inserted clip with Notion page ID."""

    id: str
    title: str
    url: str

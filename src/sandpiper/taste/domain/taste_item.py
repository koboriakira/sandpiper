from dataclasses import dataclass, field


@dataclass(frozen=True)
class TasteItem:
    title: str
    tags: list[str] = field(default_factory=list)
    comment: str | None = None
    place_page_id: str | None = None
    impression: str | None = None


@dataclass(frozen=True)
class InsertedTasteItem:
    id: str
    title: str
    tags: list[str] = field(default_factory=list)
    comment: str | None = None
    place_page_id: str | None = None
    impression: str | None = None

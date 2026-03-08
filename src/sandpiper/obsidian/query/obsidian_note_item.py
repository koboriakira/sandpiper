from dataclasses import dataclass, field


@dataclass
class ObsidianNoteItem:
    page_id: str
    title: str
    status: str | None
    tags: list[str] = field(default_factory=list)
    is_project_session: bool = False
    project_name: str | None = None
    created_date: str | None = None
    body: str = ""

from typing import Protocol

from lotion import BasePage, Lotion, notion_database

from sandpiper.obsidian.query.obsidian_note_item import ObsidianNoteItem
from sandpiper.shared.notion.databases import obsidian as obsidian_db
from sandpiper.shared.notion.databases.obsidian import (
    ObsidianCreatedDate,
    ObsidianIsProjectSession,
    ObsidianName,
    ObsidianProjectName,
    ObsidianStatus,
    ObsidianTags,
)


@notion_database(obsidian_db.DATABASE_ID)
class ObsidianPage(BasePage):
    name: ObsidianName
    status: ObsidianStatus | None = None
    tags: ObsidianTags | None = None
    is_project_session: ObsidianIsProjectSession | None = None
    project_name: ObsidianProjectName | None = None
    created_date: ObsidianCreatedDate | None = None


class ObsidianQuery(Protocol):
    def fetch(self, status: str | None = None) -> list[ObsidianNoteItem]: ...
    def fetch_with_body(self, status: str | None = None) -> list[ObsidianNoteItem]: ...


class NotionObsidianQuery:
    def __init__(self) -> None:
        self._client = Lotion.get_instance()

    def fetch(self, status: str | None = None) -> list[ObsidianNoteItem]:
        """Fetch Obsidian Inbox notes without body."""
        pages: list[ObsidianPage] = self._retrieve_pages(status)
        return [self._to_item(page) for page in pages]

    def fetch_with_body(self, status: str | None = None) -> list[ObsidianNoteItem]:
        """Fetch Obsidian Inbox notes with body content."""
        pages: list[ObsidianPage] = self._retrieve_pages(status)
        items = []
        for page in pages:
            item = self._to_item(page)
            item.body = self._get_body(page.id)
            items.append(item)
        return items

    def _retrieve_pages(self, status: str | None) -> list[ObsidianPage]:
        filter_param = None
        if status:
            filter_param = {
                "property": "ステータス",
                "select": {"equals": status},
            }
        return self._client.retrieve_database(
            obsidian_db.DATABASE_ID,
            filter_param=filter_param,
            cls=ObsidianPage,
        )

    def _get_body(self, page_id: str) -> str:
        blocks = self._client.list_blocks(page_id)
        lines = []
        for block in blocks:
            text = block.to_slack_text()
            if text:
                lines.append(text)
        return "\n".join(lines)

    def _to_item(self, page: ObsidianPage) -> ObsidianNoteItem:
        return ObsidianNoteItem(
            page_id=page.id,
            title=page.get_title_text(),
            status=page.status.selected_name if page.status else None,
            tags=page.tags.values if page.tags else [],
            is_project_session=page.is_project_session.checked if page.is_project_session else False,
            project_name=page.project_name.text if page.project_name else None,
            created_date=page.created_date.start_date if page.created_date else None,
        )

from sandpiper.obsidian.query.obsidian_note_item import ObsidianNoteItem
from sandpiper.obsidian.query.obsidian_query import ObsidianQuery


class ListObsidianNotes:
    def __init__(self, obsidian_query: ObsidianQuery) -> None:
        self._obsidian_query = obsidian_query

    def execute(self, status: str | None = None, with_body: bool = False) -> list[ObsidianNoteItem]:
        if with_body:
            return self._obsidian_query.fetch_with_body(status=status)
        return self._obsidian_query.fetch(status=status)

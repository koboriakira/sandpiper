from typing import Protocol

from lotion import Lotion  # type: ignore[import-untyped]

from sandpiper.shared.notion.databases import someday as someday_db
from sandpiper.shared.valueobject.context import Context


class IncidentalTaskQuery(Protocol):
    """「ついでに」タイミングのタスクを取得するクエリ"""

    def fetch_by_context(self, context: Context) -> list[str]:
        """指定されたコンテクストの「ついでに」タスクのタイトルを取得"""
        ...


class NotionIncidentalTaskQuery:
    """Notionを使用した「ついでに」タスククエリ"""

    def __init__(self) -> None:
        self.client = Lotion.get_instance()

    def fetch_by_context(self, context: Context) -> list[str]:
        """指定されたコンテクストの「ついでに」タスクのタイトルを取得"""
        items = self.client.retrieve_database(someday_db.DATABASE_ID)
        result = []

        for item in items:
            is_deleted = item.get_checkbox("論理削除").checked
            if is_deleted:
                continue

            timing_name = item.get_select("タイミング").selected_name
            if timing_name != "ついでに":
                continue

            context_prop = item.get_multi_select("コンテクスト")
            item_contexts = [v.name for v in context_prop.values] if context_prop else []
            if context.value not in item_contexts:
                continue

            result.append(item.get_title_text())

        return result

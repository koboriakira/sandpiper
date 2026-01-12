"""論理削除されたページを物理削除するサービス"""

from dataclasses import dataclass

from lotion import Lotion  # type: ignore[import-untyped]

from sandpiper.shared.notion.databases import project_task as project_task_db
from sandpiper.shared.notion.databases import someday as someday_db
from sandpiper.shared.notion.databases import todo as todo_db

# 論理削除プロパティを持つデータベースIDの配列
DATABASES_WITH_LOGICAL_DELETION: list[str] = [
    todo_db.DATABASE_ID,
    someday_db.DATABASE_ID,
    project_task_db.DATABASE_ID,
]


@dataclass
class ArchiveDeletedPagesResult:
    """アーカイブ結果"""

    deleted_counts: dict[str, int]

    @property
    def total_deleted_count(self) -> int:
        return sum(self.deleted_counts.values())


class ArchiveDeletedPages:
    """論理削除されたページを物理削除するサービス

    論理削除プロパティを持つデータベースから、
    論理削除プロパティが有効なページを物理削除します。
    """

    LOGICAL_DELETION_PROPERTY_NAME = "論理削除"

    def __init__(
        self,
        database_ids: list[str] | None = None,
    ) -> None:
        self.client = Lotion.get_instance()
        self.database_ids = database_ids or DATABASES_WITH_LOGICAL_DELETION

    def execute(self) -> ArchiveDeletedPagesResult:
        """論理削除されたページを物理削除する

        Returns:
            ArchiveDeletedPagesResult: データベースごとの削除件数
        """
        deleted_counts: dict[str, int] = {}

        for database_id in self.database_ids:
            deleted_count = self._archive_pages_in_database(database_id)
            deleted_counts[database_id] = deleted_count

        return ArchiveDeletedPagesResult(deleted_counts=deleted_counts)

    def _archive_pages_in_database(self, database_id: str) -> int:
        """指定されたデータベースの論理削除されたページを物理削除"""
        pages = self.client.retrieve_database(database_id)
        deleted_count = 0

        for page in pages:
            is_deleted = page.get_checkbox(self.LOGICAL_DELETION_PROPERTY_NAME).checked
            if is_deleted:
                self.client.remove_page(page.id)
                deleted_count += 1

        return deleted_count

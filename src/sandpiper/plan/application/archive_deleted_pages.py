"""論理削除されたページを物理削除するユースケース"""

from dataclasses import dataclass

from lotion import Lotion  # type: ignore[import-untyped]

from sandpiper.shared.notion.databases import someday as someday_db
from sandpiper.shared.notion.databases import todo as todo_db


@dataclass
class ArchiveDeletedPagesResult:
    """アーカイブ結果"""

    todo_deleted_count: int
    someday_deleted_count: int

    @property
    def total_deleted_count(self) -> int:
        return self.todo_deleted_count + self.someday_deleted_count


class ArchiveDeletedPages:
    """論理削除されたページを物理削除するユースケース

    TODOデータベースとサムデイリストデータベースから、
    論理削除プロパティが有効なページを物理削除します。
    """

    def __init__(self) -> None:
        self.client = Lotion.get_instance()

    def execute(self) -> ArchiveDeletedPagesResult:
        """論理削除されたページを物理削除する

        Returns:
            ArchiveDeletedPagesResult: 削除されたページ数
        """
        todo_deleted_count = self._archive_todo_pages()
        someday_deleted_count = self._archive_someday_pages()

        return ArchiveDeletedPagesResult(
            todo_deleted_count=todo_deleted_count,
            someday_deleted_count=someday_deleted_count,
        )

    def _archive_todo_pages(self) -> int:
        """TODOデータベースの論理削除されたページを物理削除"""
        pages = self.client.retrieve_database(todo_db.DATABASE_ID)
        deleted_count = 0

        for page in pages:
            is_deleted = page.get_checkbox("論理削除").checked
            if is_deleted:
                self.client.remove_page(page.id)
                deleted_count += 1

        return deleted_count

    def _archive_someday_pages(self) -> int:
        """サムデイリストデータベースの論理削除されたページを物理削除"""
        pages = self.client.retrieve_database(someday_db.DATABASE_ID)
        deleted_count = 0

        for page in pages:
            is_deleted = page.get_checkbox("論理削除").checked
            if is_deleted:
                self.client.remove_page(page.id)
                deleted_count += 1

        return deleted_count

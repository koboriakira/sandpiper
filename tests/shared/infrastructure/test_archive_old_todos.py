from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from sandpiper.shared.infrastructure.archive_old_todos import (
    DEFAULT_ARCHIVE_DAYS,
    ArchiveOldTodos,
    ArchiveOldTodosResult,
)
from sandpiper.shared.utils.date_utils import JST


class TestArchiveOldTodosResult:
    def test_archived_count_and_titles(self):
        result = ArchiveOldTodosResult(
            archived_count=3,
            archived_titles=["タスク1", "タスク2", "タスク3"],
        )
        assert result.archived_count == 3
        assert len(result.archived_titles) == 3
        assert "タスク1" in result.archived_titles

    def test_empty_result(self):
        result = ArchiveOldTodosResult(
            archived_count=0,
            archived_titles=[],
        )
        assert result.archived_count == 0
        assert len(result.archived_titles) == 0


class TestArchiveOldTodos:
    @pytest.fixture
    def mock_lotion(self):
        with patch("sandpiper.shared.infrastructure.archive_old_todos.Lotion") as mock:
            mock_instance = MagicMock()
            mock.get_instance.return_value = mock_instance
            yield mock_instance

    @pytest.fixture
    def mock_jst_now(self):
        with patch("sandpiper.shared.infrastructure.archive_old_todos.jst_now") as mock:
            mock.return_value = datetime(2024, 3, 20, 12, 0, 0, tzinfo=JST)
            yield mock

    def _create_mock_page(
        self,
        page_id: str,
        title: str,
        status: str,
        end_datetime: datetime | None,
    ) -> MagicMock:
        """テスト用のモックページを作成"""
        page = MagicMock()
        page.id = page_id
        page.get_title_text.return_value = title
        page.get_status.return_value.status_name = status
        # start も end と同じ値を設定(Lotion が start なしで end があるとエラーになるため)
        page.get_date.return_value.start = end_datetime.isoformat() if end_datetime else None
        page.get_date.return_value.end = end_datetime.isoformat() if end_datetime else None
        page.get_select.return_value.selected_name = ""
        page.get_checkbox.return_value.checked = False
        page.get_relation.return_value.id_list = []
        page.get_number.return_value.number = None
        page.get_multi_select.return_value.values = []
        page.get_text.return_value.text = ""
        return page

    def test_execute_archives_old_done_todos(self, mock_lotion, mock_jst_now):  # noqa: ARG002
        # Arrange: 10日前に完了したタスク(アーカイブ対象)
        old_end_date = datetime(2024, 3, 10, 12, 0, 0, tzinfo=JST)
        page = self._create_mock_page("page-1", "古いタスク", "Done", old_end_date)
        mock_lotion.retrieve_database.return_value = [page]

        # Act
        usecase = ArchiveOldTodos(archive_days=7)
        result = usecase.execute()

        # Assert
        assert result.archived_count == 1
        assert "古いタスク" in result.archived_titles
        mock_lotion.create_page.assert_called_once()
        mock_lotion.remove_page.assert_called_once_with("page-1")

    def test_execute_skips_non_done_todos(self, mock_lotion, mock_jst_now):  # noqa: ARG002
        # Arrange: 10日前に完了したが、ステータスがToDo
        old_end_date = datetime(2024, 3, 10, 12, 0, 0, tzinfo=JST)
        page = self._create_mock_page("page-1", "未完了タスク", "ToDo", old_end_date)
        mock_lotion.retrieve_database.return_value = [page]

        # Act
        usecase = ArchiveOldTodos(archive_days=7)
        result = usecase.execute()

        # Assert
        assert result.archived_count == 0
        mock_lotion.create_page.assert_not_called()
        mock_lotion.remove_page.assert_not_called()

    def test_execute_skips_recent_done_todos(self, mock_lotion, mock_jst_now):  # noqa: ARG002
        # Arrange: 3日前に完了(7日未満なのでアーカイブ対象外)
        recent_end_date = datetime(2024, 3, 17, 12, 0, 0, tzinfo=JST)
        page = self._create_mock_page("page-1", "最近のタスク", "Done", recent_end_date)
        mock_lotion.retrieve_database.return_value = [page]

        # Act
        usecase = ArchiveOldTodos(archive_days=7)
        result = usecase.execute()

        # Assert
        assert result.archived_count == 0
        mock_lotion.create_page.assert_not_called()
        mock_lotion.remove_page.assert_not_called()

    def test_execute_skips_done_todos_without_end_date(self, mock_lotion, mock_jst_now):  # noqa: ARG002
        # Arrange: Doneだが終了日時がない
        page = self._create_mock_page("page-1", "終了日なしタスク", "Done", None)
        mock_lotion.retrieve_database.return_value = [page]

        # Act
        usecase = ArchiveOldTodos(archive_days=7)
        result = usecase.execute()

        # Assert
        assert result.archived_count == 0
        mock_lotion.create_page.assert_not_called()
        mock_lotion.remove_page.assert_not_called()

    def test_execute_with_dry_run(self, mock_lotion, mock_jst_now):  # noqa: ARG002
        # Arrange: アーカイブ対象のタスク
        old_end_date = datetime(2024, 3, 10, 12, 0, 0, tzinfo=JST)
        page = self._create_mock_page("page-1", "古いタスク", "Done", old_end_date)
        mock_lotion.retrieve_database.return_value = [page]

        # Act
        usecase = ArchiveOldTodos(archive_days=7)
        result = usecase.execute(dry_run=True)

        # Assert: 対象として検出されるが、実際のアーカイブは行われない
        assert result.archived_count == 1
        assert "古いタスク" in result.archived_titles
        mock_lotion.create_page.assert_not_called()
        mock_lotion.remove_page.assert_not_called()

    def test_execute_with_empty_database(self, mock_lotion, mock_jst_now):  # noqa: ARG002
        # Arrange
        mock_lotion.retrieve_database.return_value = []

        # Act
        usecase = ArchiveOldTodos(archive_days=7)
        result = usecase.execute()

        # Assert
        assert result.archived_count == 0
        assert len(result.archived_titles) == 0

    def test_execute_with_custom_archive_days(self, mock_lotion, mock_jst_now):  # noqa: ARG002
        # Arrange: 5日前に完了(14日のしきい値未満)
        end_date = datetime(2024, 3, 15, 12, 0, 0, tzinfo=JST)
        page = self._create_mock_page("page-1", "5日前タスク", "Done", end_date)
        mock_lotion.retrieve_database.return_value = [page]

        # Act: 14日のしきい値でテスト
        usecase = ArchiveOldTodos(archive_days=14)
        result = usecase.execute()

        # Assert: 5日前なので14日のしきい値を超えていない
        assert result.archived_count == 0

    def test_execute_archives_multiple_old_todos(self, mock_lotion, mock_jst_now):  # noqa: ARG002
        # Arrange: 複数のアーカイブ対象タスク
        old_date1 = datetime(2024, 3, 5, 12, 0, 0, tzinfo=JST)
        old_date2 = datetime(2024, 3, 8, 12, 0, 0, tzinfo=JST)
        recent_date = datetime(2024, 3, 18, 12, 0, 0, tzinfo=JST)

        page1 = self._create_mock_page("page-1", "古いタスク1", "Done", old_date1)
        page2 = self._create_mock_page("page-2", "古いタスク2", "Done", old_date2)
        page3 = self._create_mock_page("page-3", "最近のタスク", "Done", recent_date)
        page4 = self._create_mock_page("page-4", "未完了タスク", "ToDo", old_date1)

        mock_lotion.retrieve_database.return_value = [page1, page2, page3, page4]

        # Act
        usecase = ArchiveOldTodos(archive_days=7)
        result = usecase.execute()

        # Assert
        assert result.archived_count == 2
        assert "古いタスク1" in result.archived_titles
        assert "古いタスク2" in result.archived_titles
        assert "最近のタスク" not in result.archived_titles
        assert "未完了タスク" not in result.archived_titles

    def test_default_archive_days(self):
        # Assert
        assert DEFAULT_ARCHIVE_DAYS == 7

    def test_uses_default_archive_days_when_not_provided(self, mock_lotion):  # noqa: ARG002
        # Act
        usecase = ArchiveOldTodos()

        # Assert
        assert usecase.archive_days == DEFAULT_ARCHIVE_DAYS

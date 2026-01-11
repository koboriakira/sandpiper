from unittest.mock import MagicMock, patch

import pytest

from sandpiper.shared.infrastructure.archive_deleted_pages import (
    DATABASES_WITH_LOGICAL_DELETION,
    ArchiveDeletedPages,
    ArchiveDeletedPagesResult,
)


class TestArchiveDeletedPagesResult:
    def test_total_deleted_count(self):
        result = ArchiveDeletedPagesResult(
            deleted_counts={"db1": 3, "db2": 2},
        )
        assert result.total_deleted_count == 5

    def test_total_deleted_count_with_zeros(self):
        result = ArchiveDeletedPagesResult(
            deleted_counts={"db1": 0, "db2": 0},
        )
        assert result.total_deleted_count == 0

    def test_total_deleted_count_empty(self):
        result = ArchiveDeletedPagesResult(deleted_counts={})
        assert result.total_deleted_count == 0


class TestArchiveDeletedPages:
    @pytest.fixture
    def mock_lotion(self):
        with patch("sandpiper.shared.infrastructure.archive_deleted_pages.Lotion") as mock:
            mock_instance = MagicMock()
            mock.get_instance.return_value = mock_instance
            yield mock_instance

    def test_execute_archives_deleted_pages(self, mock_lotion):
        # Arrange
        page1 = MagicMock()
        page1.id = "page-1"
        page1.get_checkbox.return_value.checked = True

        page2 = MagicMock()
        page2.id = "page-2"
        page2.get_checkbox.return_value.checked = False

        page3 = MagicMock()
        page3.id = "page-3"
        page3.get_checkbox.return_value.checked = True

        mock_lotion.retrieve_database.side_effect = [
            [page1, page2],  # First database
            [page3],  # Second database
        ]

        # Act
        usecase = ArchiveDeletedPages(database_ids=["db1", "db2"])
        result = usecase.execute()

        # Assert
        assert result.deleted_counts["db1"] == 1
        assert result.deleted_counts["db2"] == 1
        assert result.total_deleted_count == 2
        mock_lotion.remove_page.assert_any_call("page-1")
        mock_lotion.remove_page.assert_any_call("page-3")

    def test_execute_with_no_deleted_pages(self, mock_lotion):
        # Arrange
        page1 = MagicMock()
        page1.id = "page-1"
        page1.get_checkbox.return_value.checked = False

        page2 = MagicMock()
        page2.id = "page-2"
        page2.get_checkbox.return_value.checked = False

        mock_lotion.retrieve_database.side_effect = [
            [page1],
            [page2],
        ]

        # Act
        usecase = ArchiveDeletedPages(database_ids=["db1", "db2"])
        result = usecase.execute()

        # Assert
        assert result.deleted_counts["db1"] == 0
        assert result.deleted_counts["db2"] == 0
        assert result.total_deleted_count == 0
        mock_lotion.remove_page.assert_not_called()

    def test_execute_with_empty_databases(self, mock_lotion):
        # Arrange
        mock_lotion.retrieve_database.return_value = []

        # Act
        usecase = ArchiveDeletedPages(database_ids=["db1", "db2"])
        result = usecase.execute()

        # Assert
        assert result.deleted_counts["db1"] == 0
        assert result.deleted_counts["db2"] == 0
        assert result.total_deleted_count == 0

    def test_uses_default_database_ids_when_none_provided(self, mock_lotion):
        # Arrange
        mock_lotion.retrieve_database.return_value = []

        # Act
        usecase = ArchiveDeletedPages()

        # Assert
        assert usecase.database_ids == DATABASES_WITH_LOGICAL_DELETION

    def test_execute_with_custom_database_ids(self, mock_lotion):
        # Arrange
        custom_db_ids = ["custom-db-1", "custom-db-2", "custom-db-3"]
        mock_lotion.retrieve_database.return_value = []

        # Act
        usecase = ArchiveDeletedPages(database_ids=custom_db_ids)
        result = usecase.execute()

        # Assert
        assert len(result.deleted_counts) == 3
        assert mock_lotion.retrieve_database.call_count == 3

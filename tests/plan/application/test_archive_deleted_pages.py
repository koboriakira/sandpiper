from unittest.mock import MagicMock, patch

import pytest

from sandpiper.plan.application.archive_deleted_pages import (
    ArchiveDeletedPages,
    ArchiveDeletedPagesResult,
)


class TestArchiveDeletedPagesResult:
    def test_total_deleted_count(self):
        result = ArchiveDeletedPagesResult(
            todo_deleted_count=3,
            someday_deleted_count=2,
        )
        assert result.total_deleted_count == 5

    def test_total_deleted_count_with_zeros(self):
        result = ArchiveDeletedPagesResult(
            todo_deleted_count=0,
            someday_deleted_count=0,
        )
        assert result.total_deleted_count == 0


class TestArchiveDeletedPages:
    @pytest.fixture
    def mock_lotion(self):
        with patch("sandpiper.plan.application.archive_deleted_pages.Lotion") as mock:
            mock_instance = MagicMock()
            mock.get_instance.return_value = mock_instance
            yield mock_instance

    def test_execute_archives_deleted_pages(self, mock_lotion):
        # Arrange
        todo_page1 = MagicMock()
        todo_page1.id = "todo-1"
        todo_page1.get_checkbox.return_value.checked = True

        todo_page2 = MagicMock()
        todo_page2.id = "todo-2"
        todo_page2.get_checkbox.return_value.checked = False

        someday_page1 = MagicMock()
        someday_page1.id = "someday-1"
        someday_page1.get_checkbox.return_value.checked = True

        someday_page2 = MagicMock()
        someday_page2.id = "someday-2"
        someday_page2.get_checkbox.return_value.checked = True

        def retrieve_database_side_effect(database_id):
            if database_id == "2db6567a3bbf805ba379f942cdf0e264":  # TODO DB
                return [todo_page1, todo_page2]
            elif database_id == "2db6567a3bbf80a8b3f3e3560cfe380f":  # Someday DB
                return [someday_page1, someday_page2]
            return []

        mock_lotion.retrieve_database.side_effect = retrieve_database_side_effect

        # Act
        usecase = ArchiveDeletedPages()
        result = usecase.execute()

        # Assert
        assert result.todo_deleted_count == 1
        assert result.someday_deleted_count == 2
        assert result.total_deleted_count == 3
        mock_lotion.remove_page.assert_any_call("todo-1")
        mock_lotion.remove_page.assert_any_call("someday-1")
        mock_lotion.remove_page.assert_any_call("someday-2")

    def test_execute_with_no_deleted_pages(self, mock_lotion):
        # Arrange
        todo_page = MagicMock()
        todo_page.id = "todo-1"
        todo_page.get_checkbox.return_value.checked = False

        someday_page = MagicMock()
        someday_page.id = "someday-1"
        someday_page.get_checkbox.return_value.checked = False

        mock_lotion.retrieve_database.side_effect = [
            [todo_page],
            [someday_page],
        ]

        # Act
        usecase = ArchiveDeletedPages()
        result = usecase.execute()

        # Assert
        assert result.todo_deleted_count == 0
        assert result.someday_deleted_count == 0
        assert result.total_deleted_count == 0
        mock_lotion.remove_page.assert_not_called()

    def test_execute_with_empty_databases(self, mock_lotion):
        # Arrange
        mock_lotion.retrieve_database.return_value = []

        # Act
        usecase = ArchiveDeletedPages()
        result = usecase.execute()

        # Assert
        assert result.todo_deleted_count == 0
        assert result.someday_deleted_count == 0
        assert result.total_deleted_count == 0

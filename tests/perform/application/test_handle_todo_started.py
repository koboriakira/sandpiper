from unittest.mock import Mock, patch

import pytest

from sandpiper.perform.application.handle_todo_started import HandleTodoStarted
from sandpiper.perform.domain.todo import ToDo
from sandpiper.perform.domain.todo_repository import TodoRepository
from sandpiper.shared.event.todo_created import TodoStarted


class TestHandleTodoStarted:
    def setup_method(self):
        """各テストメソッドの前に実行される初期化"""
        self.mock_repository = Mock(spec=TodoRepository)
        self.handler = HandleTodoStarted(self.mock_repository)

    def test_init(self):
        """HandleTodoStartedの初期化をテスト"""
        # Arrange
        mock_repo = Mock(spec=TodoRepository)

        # Act
        handler = HandleTodoStarted(mock_repo)

        # Assert
        assert handler._todo_repository == mock_repo

    @patch('builtins.print')
    def test_call_success(self, mock_print):
        """正常なToDo開始処理をテスト"""
        # Arrange
        page_id = "test-page-123"
        event = TodoStarted(page_id=page_id)

        mock_todo = Mock(spec=ToDo)
        self.mock_repository.find.return_value = mock_todo

        # Act
        self.handler(event)

        # Assert
        mock_print.assert_called_once_with(f"ToDo started with page ID: {page_id}")
        self.mock_repository.find.assert_called_once_with(page_id)
        mock_todo.start.assert_called_once()
        self.mock_repository.save.assert_called_once_with(mock_todo)

    @patch('builtins.print')
    def test_call_with_different_page_ids(self, mock_print):
        """異なるページIDでの処理をテスト"""
        # Arrange
        test_cases = [
            "page-001",
            "another-page-xyz",
            "complex-page-id-with-numbers-123"
        ]

        for page_id in test_cases:
            # Reset mocks for each iteration
            self.mock_repository.reset_mock()
            mock_print.reset_mock()

            event = TodoStarted(page_id=page_id)
            mock_todo = Mock(spec=ToDo)
            self.mock_repository.find.return_value = mock_todo

            # Act
            self.handler(event)

            # Assert
            mock_print.assert_called_once_with(f"ToDo started with page ID: {page_id}")
            self.mock_repository.find.assert_called_once_with(page_id)
            mock_todo.start.assert_called_once()
            self.mock_repository.save.assert_called_once_with(mock_todo)

    def test_call_repository_find_error(self):
        """リポジトリのfindでエラーが発生した場合のテスト"""
        # Arrange
        page_id = "error-page-id"
        event = TodoStarted(page_id=page_id)

        self.mock_repository.find.side_effect = Exception("Repository find error")

        # Act & Assert
        with pytest.raises(Exception, match="Repository find error"):
            self.handler(event)

        # find は呼ばれるが、start と save は呼ばれない
        self.mock_repository.find.assert_called_once_with(page_id)
        self.mock_repository.save.assert_not_called()

    def test_call_todo_start_error(self):
        """ToDoのstartでエラーが発生した場合のテスト"""
        # Arrange
        page_id = "start-error-page"
        event = TodoStarted(page_id=page_id)

        mock_todo = Mock(spec=ToDo)
        mock_todo.start.side_effect = Exception("ToDo start error")
        self.mock_repository.find.return_value = mock_todo

        # Act & Assert
        with pytest.raises(Exception, match="ToDo start error"):
            self.handler(event)

        # find と start は呼ばれるが、save は呼ばれない
        self.mock_repository.find.assert_called_once_with(page_id)
        mock_todo.start.assert_called_once()
        self.mock_repository.save.assert_not_called()

    def test_call_repository_save_error(self):
        """リポジトリのsaveでエラーが発生した場合のテスト"""
        # Arrange
        page_id = "save-error-page"
        event = TodoStarted(page_id=page_id)

        mock_todo = Mock(spec=ToDo)
        self.mock_repository.find.return_value = mock_todo
        self.mock_repository.save.side_effect = Exception("Repository save error")

        # Act & Assert
        with pytest.raises(Exception, match="Repository save error"):
            self.handler(event)

        # すべてのメソッドが呼ばれるが、save でエラーになる
        self.mock_repository.find.assert_called_once_with(page_id)
        mock_todo.start.assert_called_once()
        self.mock_repository.save.assert_called_once_with(mock_todo)

    @patch('builtins.print')
    def test_call_multiple_events(self, mock_print):
        """複数のイベント処理をテスト"""
        # Arrange
        events = [
            TodoStarted(page_id="event-1"),
            TodoStarted(page_id="event-2"),
            TodoStarted(page_id="event-3")
        ]

        mock_todos = []
        for i in range(len(events)):
            mock_todo = Mock(spec=ToDo)
            mock_todos.append(mock_todo)

        self.mock_repository.find.side_effect = mock_todos

        # Act
        for event in events:
            self.handler(event)

        # Assert
        assert self.mock_repository.find.call_count == len(events)
        assert self.mock_repository.save.call_count == len(events)

        for i, event in enumerate(events):
            # findの呼び出し確認
            assert self.mock_repository.find.call_args_list[i][0][0] == event.page_id
            # startの呼び出し確認
            mock_todos[i].start.assert_called_once()
            # saveの呼び出し確認
            assert self.mock_repository.save.call_args_list[i][0][0] == mock_todos[i]
        # printの呼び出し確認
        expected_calls = [f"ToDo started with page ID: {event.page_id}" for event in events]
        actual_calls = [call.args[0] for call in mock_print.call_args_list]
        assert actual_calls == expected_calls

    @patch('builtins.print')
    def test_call_with_empty_page_id(self, mock_print):
        """空のページIDでの処理をテスト"""
        # Arrange
        page_id = ""
        event = TodoStarted(page_id=page_id)

        mock_todo = Mock(spec=ToDo)
        self.mock_repository.find.return_value = mock_todo

        # Act
        self.handler(event)

        # Assert
        mock_print.assert_called_once_with("ToDo started with page ID: ")
        self.mock_repository.find.assert_called_once_with("")
        mock_todo.start.assert_called_once()
        self.mock_repository.save.assert_called_once_with(mock_todo)

    def test_handler_immutability(self):
        """ハンドラーのイミュータブルな動作をテスト"""
        # Arrange
        original_repo = self.handler._todo_repository
        page_id = "immutable-test"
        event = TodoStarted(page_id=page_id)

        mock_todo = Mock(spec=ToDo)
        self.mock_repository.find.return_value = mock_todo

        # Act
        self.handler(event)

        # Assert - ハンドラーのリポジトリは変更されない
        assert self.handler._todo_repository == original_repo
        assert self.handler._todo_repository is original_repo

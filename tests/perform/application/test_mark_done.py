from unittest.mock import Mock

import pytest

from sandpiper.app.message_dispatcher import MessageDispatcher
from sandpiper.perform.application.mark_done import MarkDone, MarkDoneResult
from sandpiper.perform.domain.todo_repository import TodoRepository
from sandpiper.shared.event.todo_completed import TodoCompleted


class TestMarkDone:
    def setup_method(self):
        self.mock_repository = Mock(spec=TodoRepository)
        self.mock_dispatcher = Mock(spec=MessageDispatcher)
        self.mark_done = MarkDone(self.mock_repository, self.mock_dispatcher)

    def test_init(self):
        """MarkDoneの初期化をテスト"""
        repository = Mock(spec=TodoRepository)
        dispatcher = Mock(spec=MessageDispatcher)

        mark_done = MarkDone(repository, dispatcher)

        assert mark_done._todo_repository == repository
        assert mark_done._dispatcher == dispatcher

    def test_execute_no_in_progress_todos(self):
        """InProgress中のToDoがない場合のテスト"""
        # Arrange
        self.mock_repository.find_in_progress.return_value = []

        # Act
        result = self.mark_done.execute()

        # Assert
        assert isinstance(result, MarkDoneResult)
        assert result.completed_count == 0
        assert result.completed_titles == []
        self.mock_repository.find_in_progress.assert_called_once()
        self.mock_repository.save.assert_not_called()
        self.mock_dispatcher.publish.assert_not_called()

    def test_execute_single_in_progress_todo(self):
        """1件のInProgress中のToDoを完了するテスト"""
        # Arrange
        mock_todo = Mock()
        mock_todo.id = "test-page-id-1"
        mock_todo.title = "テストタスク1"
        self.mock_repository.find_in_progress.return_value = [mock_todo]

        # Act
        result = self.mark_done.execute()

        # Assert
        assert result.completed_count == 1
        assert result.completed_titles == ["テストタスク1"]
        mock_todo.complete.assert_called_once()
        self.mock_repository.save.assert_called_once_with(mock_todo)

        # TodoCompletedイベントが発行されることを確認
        self.mock_dispatcher.publish.assert_called_once()
        published_event = self.mock_dispatcher.publish.call_args[0][0]
        assert isinstance(published_event, TodoCompleted)
        assert published_event.page_id == "test-page-id-1"
        assert published_event.title == "テストタスク1"

    def test_execute_multiple_in_progress_todos(self):
        """複数のInProgress中のToDoを完了するテスト"""
        # Arrange
        mock_todo1 = Mock()
        mock_todo1.id = "test-page-id-1"
        mock_todo1.title = "テストタスク1"

        mock_todo2 = Mock()
        mock_todo2.id = "test-page-id-2"
        mock_todo2.title = "テストタスク2"

        mock_todo3 = Mock()
        mock_todo3.id = "test-page-id-3"
        mock_todo3.title = "テストタスク3"

        self.mock_repository.find_in_progress.return_value = [mock_todo1, mock_todo2, mock_todo3]

        # Act
        result = self.mark_done.execute()

        # Assert
        assert result.completed_count == 3
        assert result.completed_titles == ["テストタスク1", "テストタスク2", "テストタスク3"]

        # 各ToDoのcomplete()が呼ばれたことを確認
        mock_todo1.complete.assert_called_once()
        mock_todo2.complete.assert_called_once()
        mock_todo3.complete.assert_called_once()

        # save()が3回呼ばれたことを確認
        assert self.mock_repository.save.call_count == 3

        # TodoCompletedイベントが3回発行されたことを確認
        assert self.mock_dispatcher.publish.call_count == 3

    def test_execute_find_in_progress_raises_exception(self):
        """find_in_progress()で例外が発生した場合のテスト"""
        # Arrange
        self.mock_repository.find_in_progress.side_effect = Exception("Find failed")

        # Act & Assert
        with pytest.raises(Exception, match="Find failed"):
            self.mark_done.execute()

        # find_in_progressのみ呼ばれ、他は呼ばれないことを確認
        self.mock_repository.find_in_progress.assert_called_once()
        self.mock_repository.save.assert_not_called()
        self.mock_dispatcher.publish.assert_not_called()

    def test_execute_save_raises_exception(self):
        """repository.save()で例外が発生した場合のテスト"""
        # Arrange
        mock_todo = Mock()
        mock_todo.id = "test-page-id"
        mock_todo.title = "保存失敗タスク"
        self.mock_repository.find_in_progress.return_value = [mock_todo]
        self.mock_repository.save.side_effect = Exception("Save failed")

        # Act & Assert
        with pytest.raises(Exception, match="Save failed"):
            self.mark_done.execute()

        # complete()は呼ばれたが、publishは呼ばれないことを確認
        mock_todo.complete.assert_called_once()
        self.mock_repository.save.assert_called_once_with(mock_todo)
        self.mock_dispatcher.publish.assert_not_called()


class TestMarkDoneResult:
    def test_result_dataclass(self):
        """MarkDoneResultのデータクラスをテスト"""
        result = MarkDoneResult(
            completed_count=2,
            completed_titles=["タスク1", "タスク2"],
        )

        assert result.completed_count == 2
        assert result.completed_titles == ["タスク1", "タスク2"]

    def test_result_empty(self):
        """空の結果のテスト"""
        result = MarkDoneResult(
            completed_count=0,
            completed_titles=[],
        )

        assert result.completed_count == 0
        assert result.completed_titles == []

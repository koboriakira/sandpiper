from unittest.mock import Mock
import pytest

from sandpiper.app.message_dispatcher import MessageDispatcher
from sandpiper.perform.application.complete_todo import CompleteTodo
from sandpiper.perform.domain.todo_repository import TodoRepository
from sandpiper.shared.event.todo_completed import TodoCompleted


class TestCompleteTodo:
    def setup_method(self):
        self.mock_repository = Mock(spec=TodoRepository)
        self.mock_dispatcher = Mock(spec=MessageDispatcher)
        self.complete_todo = CompleteTodo(self.mock_repository, self.mock_dispatcher)

    def test_init(self):
        """CompleteTodoの初期化をテスト"""
        repository = Mock(spec=TodoRepository)
        dispatcher = Mock(spec=MessageDispatcher)
        
        complete_todo = CompleteTodo(repository, dispatcher)
        
        assert complete_todo._todo_repository == repository
        assert complete_todo._dispatcher == dispatcher

    def test_execute_complete_todo_success(self):
        """ToDo完了の正常なexecuteをテスト"""
        # Arrange
        page_id = "test-page-id"
        mock_todo = Mock()
        mock_todo.title = "テストタスク"
        self.mock_repository.find.return_value = mock_todo
        
        # Act
        self.complete_todo.execute(page_id)
        
        # Assert
        self.mock_repository.find.assert_called_once_with(page_id)
        mock_todo.complete.assert_called_once()
        self.mock_repository.save.assert_called_once_with(mock_todo)
        
        # TodoCompletedイベントが発行されることを確認
        self.mock_dispatcher.publish.assert_called_once()
        published_event = self.mock_dispatcher.publish.call_args[0][0]
        assert isinstance(published_event, TodoCompleted)
        assert published_event.page_id == page_id
        assert published_event.title == "テストタスク"

    def test_execute_with_empty_title(self):
        """空のタイトルを持つToDoの完了をテスト"""
        # Arrange
        page_id = "test-page-empty-title"
        mock_todo = Mock()
        mock_todo.title = ""
        self.mock_repository.find.return_value = mock_todo
        
        # Act
        self.complete_todo.execute(page_id)
        
        # Assert
        self.mock_repository.find.assert_called_once_with(page_id)
        mock_todo.complete.assert_called_once()
        self.mock_repository.save.assert_called_once_with(mock_todo)
        
        # TodoCompletedイベントが空タイトルで発行されることを確認
        self.mock_dispatcher.publish.assert_called_once()
        published_event = self.mock_dispatcher.publish.call_args[0][0]
        assert isinstance(published_event, TodoCompleted)
        assert published_event.page_id == page_id
        assert published_event.title == ""

    def test_execute_todo_complete_raises_exception(self):
        """todo.complete()で例外が発生した場合のテスト"""
        # Arrange
        page_id = "test-page-exception"
        mock_todo = Mock()
        mock_todo.title = "例外タスク"
        mock_todo.complete.side_effect = Exception("Complete failed")
        self.mock_repository.find.return_value = mock_todo
        
        # Act & Assert
        with pytest.raises(Exception, match="Complete failed"):
            self.complete_todo.execute(page_id)
        
        # findは呼ばれたが、saveとpublishは呼ばれないことを確認
        self.mock_repository.find.assert_called_once_with(page_id)
        mock_todo.complete.assert_called_once()
        self.mock_repository.save.assert_not_called()
        self.mock_dispatcher.publish.assert_not_called()

    def test_execute_repository_save_raises_exception(self):
        """repository.save()で例外が発生した場合のテスト"""
        # Arrange
        page_id = "test-page-save-exception"
        mock_todo = Mock()
        mock_todo.title = "保存失敗タスク"
        self.mock_repository.find.return_value = mock_todo
        self.mock_repository.save.side_effect = Exception("Save failed")
        
        # Act & Assert
        with pytest.raises(Exception, match="Save failed"):
            self.complete_todo.execute(page_id)
        
        # complete()は呼ばれたが、publishは呼ばれないことを確認
        self.mock_repository.find.assert_called_once_with(page_id)
        mock_todo.complete.assert_called_once()
        self.mock_repository.save.assert_called_once_with(mock_todo)
        self.mock_dispatcher.publish.assert_not_called()

    def test_execute_repository_find_raises_exception(self):
        """repository.find()で例外が発生した場合のテスト"""
        # Arrange
        page_id = "test-page-find-exception"
        self.mock_repository.find.side_effect = Exception("Todo not found")
        
        # Act & Assert
        with pytest.raises(Exception, match="Todo not found"):
            self.complete_todo.execute(page_id)
        
        # findのみ呼ばれ、他は呼ばれないことを確認
        self.mock_repository.find.assert_called_once_with(page_id)
        self.mock_repository.save.assert_not_called()
        self.mock_dispatcher.publish.assert_not_called()

    def test_execute_dispatcher_publish_raises_exception(self):
        """dispatcher.publish()で例外が発生した場合のテスト"""
        # Arrange
        page_id = "test-page-publish-exception"
        mock_todo = Mock()
        mock_todo.title = "発行失敗タスク"
        self.mock_repository.find.return_value = mock_todo
        self.mock_dispatcher.publish.side_effect = Exception("Publish failed")
        
        # Act & Assert
        with pytest.raises(Exception, match="Publish failed"):
            self.complete_todo.execute(page_id)
        
        # save()まで呼ばれることを確認
        self.mock_repository.find.assert_called_once_with(page_id)
        mock_todo.complete.assert_called_once()
        self.mock_repository.save.assert_called_once_with(mock_todo)
        self.mock_dispatcher.publish.assert_called_once()

    def test_execute_with_none_todo_title(self):
        """todo.titleがNoneの場合のテスト"""
        # Arrange
        page_id = "test-page-none-title"
        mock_todo = Mock()
        mock_todo.title = None
        self.mock_repository.find.return_value = mock_todo
        
        # Act
        self.complete_todo.execute(page_id)
        
        # Assert
        self.mock_repository.find.assert_called_once_with(page_id)
        mock_todo.complete.assert_called_once()
        self.mock_repository.save.assert_called_once_with(mock_todo)
        
        # TodoCompletedイベントがNoneタイトルで発行されることを確認
        self.mock_dispatcher.publish.assert_called_once()
        published_event = self.mock_dispatcher.publish.call_args[0][0]
        assert isinstance(published_event, TodoCompleted)
        assert published_event.page_id == page_id
        assert published_event.title is None
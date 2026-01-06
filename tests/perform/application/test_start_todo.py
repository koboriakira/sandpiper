from unittest.mock import Mock

import pytest

from sandpiper.perform.application.start_todo import StartTodo
from sandpiper.perform.domain.todo_repository import TodoRepository
from sandpiper.plan.domain.project_task import InsertedProjectTask
from sandpiper.plan.domain.project_task_repository import ProjectTaskRepository
from sandpiper.shared.valueobject.todo_status_enum import ToDoStatusEnum


class TestStartTodo:
    def setup_method(self):
        self.mock_repository = Mock(spec=TodoRepository)
        self.mock_project_task_repository = Mock(spec=ProjectTaskRepository)
        self.start_todo = StartTodo(self.mock_repository, self.mock_project_task_repository)

    def test_init(self):
        """StartTodoの初期化をテスト"""
        repository = Mock(spec=TodoRepository)
        project_task_repository = Mock(spec=ProjectTaskRepository)

        start_todo = StartTodo(repository, project_task_repository)

        assert start_todo._todo_repository == repository
        assert start_todo._project_task_repository == project_task_repository

    def test_execute_start_todo_success_without_project_task(self):
        """プロジェクトタスクなしのToDo開始の正常なexecuteをテスト"""
        # Arrange
        page_id = "test-page-id"
        mock_todo = Mock()
        mock_todo.project_task_page_id = None
        self.mock_repository.find.return_value = mock_todo

        # Act
        self.start_todo.execute(page_id)

        # Assert
        self.mock_repository.find.assert_called_once_with(page_id)
        mock_todo.start.assert_called_once()
        self.mock_repository.save.assert_called_once_with(mock_todo)
        self.mock_project_task_repository.find.assert_not_called()
        self.mock_project_task_repository.update_status.assert_not_called()

    def test_execute_start_todo_success_with_project_task(self):
        """プロジェクトタスクありのToDo開始の正常なexecuteをテスト"""
        # Arrange
        page_id = "test-page-id"
        project_task_page_id = "project-task-page-id"
        mock_todo = Mock()
        mock_todo.project_task_page_id = project_task_page_id
        self.mock_repository.find.return_value = mock_todo
        mock_project_task = InsertedProjectTask(
            id=project_task_page_id,
            title="Test Project Task",
            status=ToDoStatusEnum.TODO,
            project_id="project-id",
        )
        self.mock_project_task_repository.find.return_value = mock_project_task

        # Act
        self.start_todo.execute(page_id)

        # Assert
        self.mock_repository.find.assert_called_once_with(page_id)
        mock_todo.start.assert_called_once()
        self.mock_repository.save.assert_called_once_with(mock_todo)
        self.mock_project_task_repository.find.assert_called_once_with(project_task_page_id)
        self.mock_project_task_repository.update_status.assert_called_once_with(
            project_task_page_id, ToDoStatusEnum.IN_PROGRESS
        )

    def test_execute_start_todo_with_project_task_already_in_progress(self):
        """プロジェクトタスクがすでにInProgressの場合のテスト"""
        # Arrange
        page_id = "test-page-id"
        project_task_page_id = "project-task-page-id"
        mock_todo = Mock()
        mock_todo.project_task_page_id = project_task_page_id
        self.mock_repository.find.return_value = mock_todo
        mock_project_task = InsertedProjectTask(
            id=project_task_page_id,
            title="Test Project Task",
            status=ToDoStatusEnum.IN_PROGRESS,  # すでにInProgress
            project_id="project-id",
        )
        self.mock_project_task_repository.find.return_value = mock_project_task

        # Act
        self.start_todo.execute(page_id)

        # Assert
        self.mock_repository.find.assert_called_once_with(page_id)
        mock_todo.start.assert_called_once()
        self.mock_repository.save.assert_called_once_with(mock_todo)
        self.mock_project_task_repository.find.assert_called_once_with(project_task_page_id)
        self.mock_project_task_repository.update_status.assert_not_called()

    def test_execute_repository_find_raises_exception(self):
        """repository.find()で例外が発生した場合のテスト"""
        # Arrange
        page_id = "test-page-find-exception"
        self.mock_repository.find.side_effect = Exception("Todo not found")

        # Act & Assert
        with pytest.raises(Exception, match="Todo not found"):
            self.start_todo.execute(page_id)

        # findのみ呼ばれ、他は呼ばれないことを確認
        self.mock_repository.find.assert_called_once_with(page_id)
        self.mock_repository.save.assert_not_called()
        self.mock_project_task_repository.find.assert_not_called()
        self.mock_project_task_repository.update_status.assert_not_called()

    def test_execute_todo_start_raises_exception(self):
        """todo.start()で例外が発生した場合のテスト"""
        # Arrange
        page_id = "test-page-start-exception"
        mock_todo = Mock()
        mock_todo.project_task_page_id = None
        mock_todo.start.side_effect = Exception("Start failed")
        self.mock_repository.find.return_value = mock_todo

        # Act & Assert
        with pytest.raises(Exception, match="Start failed"):
            self.start_todo.execute(page_id)

        # findは呼ばれたが、saveは呼ばれないことを確認
        self.mock_repository.find.assert_called_once_with(page_id)
        mock_todo.start.assert_called_once()
        self.mock_repository.save.assert_not_called()
        self.mock_project_task_repository.find.assert_not_called()
        self.mock_project_task_repository.update_status.assert_not_called()

    def test_execute_repository_save_raises_exception(self):
        """repository.save()で例外が発生した場合のテスト"""
        # Arrange
        page_id = "test-page-save-exception"
        mock_todo = Mock()
        mock_todo.project_task_page_id = None
        self.mock_repository.find.return_value = mock_todo
        self.mock_repository.save.side_effect = Exception("Save failed")

        # Act & Assert
        with pytest.raises(Exception, match="Save failed"):
            self.start_todo.execute(page_id)

        # start()は呼ばれることを確認
        self.mock_repository.find.assert_called_once_with(page_id)
        mock_todo.start.assert_called_once()
        self.mock_repository.save.assert_called_once_with(mock_todo)
        self.mock_project_task_repository.find.assert_not_called()
        self.mock_project_task_repository.update_status.assert_not_called()

    def test_execute_with_different_page_ids(self):
        """異なるpage_idでの実行をテスト"""
        # Arrange
        page_id1 = "test-page-1"
        page_id2 = "test-page-2"
        mock_todo1 = Mock()
        mock_todo1.project_task_page_id = None
        mock_todo2 = Mock()
        mock_todo2.project_task_page_id = None

        # 異なるページIDで異なるtoDoが返されるようにモック設定
        self.mock_repository.find.side_effect = lambda pid: mock_todo1 if pid == page_id1 else mock_todo2

        # Act
        self.start_todo.execute(page_id1)
        self.start_todo.execute(page_id2)

        # Assert
        assert self.mock_repository.find.call_count == 2
        self.mock_repository.find.assert_any_call(page_id1)
        self.mock_repository.find.assert_any_call(page_id2)

        mock_todo1.start.assert_called_once()
        mock_todo2.start.assert_called_once()

        assert self.mock_repository.save.call_count == 2
        self.mock_repository.save.assert_any_call(mock_todo1)
        self.mock_repository.save.assert_any_call(mock_todo2)
        self.mock_project_task_repository.find.assert_not_called()
        self.mock_project_task_repository.update_status.assert_not_called()

    def test_execute_multiple_times_same_todo(self):
        """同一toDoに対して複数回実行をテスト"""
        # Arrange
        page_id = "test-page-multiple"
        mock_todo = Mock()
        mock_todo.project_task_page_id = None
        self.mock_repository.find.return_value = mock_todo

        # Act
        self.start_todo.execute(page_id)
        self.start_todo.execute(page_id)

        # Assert
        assert self.mock_repository.find.call_count == 2
        assert mock_todo.start.call_count == 2
        assert self.mock_repository.save.call_count == 2

        # 両回とも同じ引数で呼ばれることを確認
        for call in self.mock_repository.find.call_args_list:
            assert call[0][0] == page_id
        for call in self.mock_repository.save.call_args_list:
            assert call[0][0] == mock_todo
        self.mock_project_task_repository.find.assert_not_called()
        self.mock_project_task_repository.update_status.assert_not_called()

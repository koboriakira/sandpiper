"""プロジェクトタスク作成ユースケースのテスト"""

from unittest.mock import Mock

from sandpiper.plan.application.create_project_task import CreateProjectTask, CreateProjectTaskRequest
from sandpiper.plan.domain.project_task import InsertedProjectTask, ProjectTask
from sandpiper.shared.valueobject.todo_status_enum import ToDoStatusEnum


class TestCreateProjectTask:
    def setup_method(self):
        """各テストメソッドの前に実行されるセットアップ"""
        self.mock_repository = Mock()
        self.use_case = CreateProjectTask(project_task_repository=self.mock_repository)

    def test_execute_creates_project_task_with_default_status(self):
        """デフォルトステータス(TODO)でプロジェクトタスクを作成"""
        # Arrange
        request = CreateProjectTaskRequest(
            title="新機能開発",
            project_id="project-123",
        )
        expected_inserted = InsertedProjectTask(
            id="task-456",
            title="新機能開発",
            status=ToDoStatusEnum.TODO,
            project_id="project-123",
        )
        self.mock_repository.save.return_value = expected_inserted

        # Act
        self.use_case.execute(request)

        # Assert
        self.mock_repository.save.assert_called_once()
        saved_task = self.mock_repository.save.call_args[0][0]
        assert isinstance(saved_task, ProjectTask)
        assert saved_task.title == "新機能開発"
        assert saved_task.status == ToDoStatusEnum.TODO
        assert saved_task.project_id == "project-123"

    def test_execute_creates_project_task_with_custom_status(self):
        """カスタムステータスでプロジェクトタスクを作成"""
        # Arrange
        request = CreateProjectTaskRequest(
            title="バグ修正タスク",
            project_id="project-789",
            status=ToDoStatusEnum.IN_PROGRESS,
        )
        expected_inserted = InsertedProjectTask(
            id="task-abc",
            title="バグ修正タスク",
            status=ToDoStatusEnum.IN_PROGRESS,
            project_id="project-789",
        )
        self.mock_repository.save.return_value = expected_inserted

        # Act
        self.use_case.execute(request)

        # Assert
        self.mock_repository.save.assert_called_once()
        saved_task = self.mock_repository.save.call_args[0][0]
        assert saved_task.title == "バグ修正タスク"
        assert saved_task.status == ToDoStatusEnum.IN_PROGRESS
        assert saved_task.project_id == "project-789"

    def test_execute_with_done_status(self):
        """DONE状態でプロジェクトタスクを作成"""
        # Arrange
        request = CreateProjectTaskRequest(
            title="完了済みタスク",
            project_id="project-complete",
            status=ToDoStatusEnum.DONE,
        )
        expected_inserted = InsertedProjectTask(
            id="task-done",
            title="完了済みタスク",
            status=ToDoStatusEnum.DONE,
            project_id="project-complete",
        )
        self.mock_repository.save.return_value = expected_inserted

        # Act
        self.use_case.execute(request)

        # Assert
        saved_task = self.mock_repository.save.call_args[0][0]
        assert saved_task.status == ToDoStatusEnum.DONE

    def test_execute_calls_repository_save_exactly_once(self):
        """リポジトリのsaveが1回だけ呼ばれることを確認"""
        # Arrange
        request = CreateProjectTaskRequest(
            title="テストタスク",
            project_id="project-test",
        )
        self.mock_repository.save.return_value = InsertedProjectTask(
            id="task-test",
            title="テストタスク",
            status=ToDoStatusEnum.TODO,
            project_id="project-test",
        )

        # Act
        self.use_case.execute(request)

        # Assert
        assert self.mock_repository.save.call_count == 1

"""TODOからプロジェクトへの変換ユースケースのテスト"""

from datetime import date
from unittest.mock import Mock, patch

from sandpiper.plan.application.convert_to_project import ConvertToProject, ConvertToProjectResult
from sandpiper.plan.domain.project import InsertedProject, Project
from sandpiper.plan.domain.project_task import InsertedProjectTask, ProjectTask
from sandpiper.plan.domain.todo import ToDo
from sandpiper.shared.valueobject.todo_status_enum import ToDoStatusEnum


class TestConvertToProject:
    def setup_method(self):
        """各テストメソッドの前に実行されるセットアップ"""
        self.mock_todo_repository = Mock()
        self.mock_project_repository = Mock()
        self.mock_project_task_repository = Mock()
        self.use_case = ConvertToProject(
            todo_repository=self.mock_todo_repository,
            project_repository=self.mock_project_repository,
            project_task_repository=self.mock_project_task_repository,
        )

    @patch("sandpiper.plan.application.convert_to_project.jst_today")
    def test_execute_converts_todo_to_project(self, mock_jst_today):
        """TODOをプロジェクトに変換できること"""
        # Arrange
        mock_jst_today.return_value = date(2024, 3, 15)
        todo = ToDo(title="新機能開発")
        self.mock_todo_repository.find.return_value = todo

        inserted_project = InsertedProject(
            id="project-123",
            name="新機能開発",
            start_date=date(2024, 3, 15),
        )
        self.mock_project_repository.save.return_value = inserted_project

        inserted_project_task = InsertedProjectTask(
            id="task-456",
            title="新機能開発",
            status=ToDoStatusEnum.TODO,
            project_id="project-123",
        )
        self.mock_project_task_repository.save.return_value = inserted_project_task

        # Act
        result = self.use_case.execute(page_id="todo-page-id")

        # Assert
        assert result.project_id == "project-123"
        assert result.project_task_id == "task-456"
        assert result.title == "新機能開発"

    @patch("sandpiper.plan.application.convert_to_project.jst_today")
    def test_execute_creates_project_with_today_start_date(self, mock_jst_today):
        """プロジェクトの開始日が今日の日付であること"""
        # Arrange
        mock_jst_today.return_value = date(2024, 6, 1)
        todo = ToDo(title="リファクタリング")
        self.mock_todo_repository.find.return_value = todo

        inserted_project = InsertedProject(
            id="project-new",
            name="リファクタリング",
            start_date=date(2024, 6, 1),
        )
        self.mock_project_repository.save.return_value = inserted_project
        self.mock_project_task_repository.save.return_value = InsertedProjectTask(
            id="task-new",
            title="リファクタリング",
            status=ToDoStatusEnum.TODO,
            project_id="project-new",
        )

        # Act
        self.use_case.execute(page_id="todo-page-id")

        # Assert
        saved_project = self.mock_project_repository.save.call_args[0][0]
        assert isinstance(saved_project, Project)
        assert saved_project.start_date == date(2024, 6, 1)
        assert saved_project.end_date is None

    @patch("sandpiper.plan.application.convert_to_project.jst_today")
    def test_execute_creates_project_task_with_project_relation(self, mock_jst_today):
        """プロジェクトタスクがプロジェクトのリレーションを持つこと"""
        # Arrange
        mock_jst_today.return_value = date(2024, 3, 15)
        todo = ToDo(title="バグ修正")
        self.mock_todo_repository.find.return_value = todo

        inserted_project = InsertedProject(
            id="project-bug",
            name="バグ修正",
            start_date=date(2024, 3, 15),
        )
        self.mock_project_repository.save.return_value = inserted_project
        self.mock_project_task_repository.save.return_value = InsertedProjectTask(
            id="task-bug",
            title="バグ修正",
            status=ToDoStatusEnum.TODO,
            project_id="project-bug",
        )

        # Act
        self.use_case.execute(page_id="todo-page-id")

        # Assert
        saved_project_task = self.mock_project_task_repository.save.call_args[0][0]
        assert isinstance(saved_project_task, ProjectTask)
        assert saved_project_task.project_id == "project-bug"
        assert saved_project_task.status == ToDoStatusEnum.TODO

    @patch("sandpiper.plan.application.convert_to_project.jst_today")
    def test_execute_uses_same_title_for_project_and_task(self, mock_jst_today):
        """プロジェクトとプロジェクトタスクが同じタイトルを持つこと"""
        # Arrange
        mock_jst_today.return_value = date(2024, 3, 15)
        todo = ToDo(title="ドキュメント整備")
        self.mock_todo_repository.find.return_value = todo

        inserted_project = InsertedProject(
            id="project-docs",
            name="ドキュメント整備",
            start_date=date(2024, 3, 15),
        )
        self.mock_project_repository.save.return_value = inserted_project
        self.mock_project_task_repository.save.return_value = InsertedProjectTask(
            id="task-docs",
            title="ドキュメント整備",
            status=ToDoStatusEnum.TODO,
            project_id="project-docs",
        )

        # Act
        self.use_case.execute(page_id="todo-page-id")

        # Assert
        saved_project = self.mock_project_repository.save.call_args[0][0]
        saved_project_task = self.mock_project_task_repository.save.call_args[0][0]
        assert saved_project.name == "ドキュメント整備"
        assert saved_project_task.title == "ドキュメント整備"

    @patch("sandpiper.plan.application.convert_to_project.jst_today")
    def test_execute_returns_convert_to_project_result(self, mock_jst_today):
        """変換結果がConvertToProjectResultで返されること"""
        # Arrange
        mock_jst_today.return_value = date(2024, 3, 15)
        todo = ToDo(title="テスト追加")
        self.mock_todo_repository.find.return_value = todo

        inserted_project = InsertedProject(
            id="proj-test",
            name="テスト追加",
            start_date=date(2024, 3, 15),
        )
        self.mock_project_repository.save.return_value = inserted_project
        self.mock_project_task_repository.save.return_value = InsertedProjectTask(
            id="task-test",
            title="テスト追加",
            status=ToDoStatusEnum.TODO,
            project_id="proj-test",
        )

        # Act
        result = self.use_case.execute(page_id="todo-page-id")

        # Assert
        assert isinstance(result, ConvertToProjectResult)
        assert result.project_id == "proj-test"
        assert result.project_task_id == "task-test"
        assert result.title == "テスト追加"

    @patch("sandpiper.plan.application.convert_to_project.jst_today")
    def test_execute_calls_repositories_in_correct_order(self, mock_jst_today):
        """リポジトリが正しい順序で呼ばれること"""
        # Arrange
        mock_jst_today.return_value = date(2024, 3, 15)
        todo = ToDo(title="順序テスト")
        self.mock_todo_repository.find.return_value = todo

        inserted_project = InsertedProject(
            id="proj-order",
            name="順序テスト",
            start_date=date(2024, 3, 15),
        )
        self.mock_project_repository.save.return_value = inserted_project
        self.mock_project_task_repository.save.return_value = InsertedProjectTask(
            id="task-order",
            title="順序テスト",
            status=ToDoStatusEnum.TODO,
            project_id="proj-order",
        )

        # Act
        self.use_case.execute(page_id="todo-page-id")

        # Assert
        # 1. TODOを取得
        self.mock_todo_repository.find.assert_called_once_with("todo-page-id")
        # 2. プロジェクトを作成
        self.mock_project_repository.save.assert_called_once()
        # 3. プロジェクトタスクを作成
        self.mock_project_task_repository.save.assert_called_once()

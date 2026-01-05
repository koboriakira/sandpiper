"""プロジェクトタスクドメインモデルのテスト"""

from sandpiper.plan.domain.project_task import InsertedProjectTask, ProjectTask
from sandpiper.shared.valueobject.todo_status_enum import ToDoStatusEnum


class TestProjectTask:
    def test_project_task_creation_with_default_status(self):
        """プロジェクトタスクの作成(デフォルトステータス)"""
        # Arrange & Act
        project_task = ProjectTask(
            title="新機能実装",
            status=ToDoStatusEnum.TODO,
            project_id="project-123",
        )

        # Assert
        assert project_task.title == "新機能実装"
        assert project_task.status == ToDoStatusEnum.TODO
        assert project_task.project_id == "project-123"

    def test_project_task_creation_with_in_progress_status(self):
        """プロジェクトタスクの作成(進行中ステータス)"""
        # Arrange & Act
        project_task = ProjectTask(
            title="バグ調査",
            status=ToDoStatusEnum.IN_PROGRESS,
            project_id="project-456",
        )

        # Assert
        assert project_task.status == ToDoStatusEnum.IN_PROGRESS

    def test_project_task_creation_with_done_status(self):
        """プロジェクトタスクの作成(完了ステータス)"""
        # Arrange & Act
        project_task = ProjectTask(
            title="レビュー対応",
            status=ToDoStatusEnum.DONE,
            project_id="project-789",
        )

        # Assert
        assert project_task.status == ToDoStatusEnum.DONE

    def test_project_task_dataclass_fields(self):
        """ProjectTaskがdataclassとして正しく定義されていることをテスト"""
        # Arrange
        project_task = ProjectTask(
            title="テストタスク",
            status=ToDoStatusEnum.TODO,
            project_id="project-test",
        )

        # Assert
        assert hasattr(project_task, "__dataclass_fields__")
        assert "title" in project_task.__dataclass_fields__
        assert "status" in project_task.__dataclass_fields__
        assert "project_id" in project_task.__dataclass_fields__


class TestInsertedProjectTask:
    def test_inserted_project_task_creation(self):
        """挿入されたプロジェクトタスクの作成"""
        # Arrange & Act
        inserted = InsertedProjectTask(
            id="task-abc123",
            title="新機能実装",
            status=ToDoStatusEnum.TODO,
            project_id="project-xyz",
        )

        # Assert
        assert inserted.id == "task-abc123"
        assert inserted.title == "新機能実装"
        assert inserted.status == ToDoStatusEnum.TODO
        assert inserted.project_id == "project-xyz"

    def test_inserted_project_task_dataclass_fields(self):
        """InsertedProjectTaskがdataclassとして正しく定義されていることをテスト"""
        # Arrange
        inserted = InsertedProjectTask(
            id="task-test",
            title="テストタスク",
            status=ToDoStatusEnum.TODO,
            project_id="project-test",
        )

        # Assert
        assert hasattr(inserted, "__dataclass_fields__")
        assert "id" in inserted.__dataclass_fields__
        assert "title" in inserted.__dataclass_fields__
        assert "status" in inserted.__dataclass_fields__
        assert "project_id" in inserted.__dataclass_fields__

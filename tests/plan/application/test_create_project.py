from datetime import date
from unittest.mock import Mock

from sandpiper.plan.application.create_project import CreateProject, CreateProjectRequest
from sandpiper.plan.domain.project import InsertedProject, Project
from sandpiper.plan.domain.project_repository import ProjectRepository
from sandpiper.plan.domain.project_task import ProjectTask
from sandpiper.plan.domain.project_task_repository import ProjectTaskRepository
from sandpiper.shared.valueobject.todo_status_enum import ToDoStatusEnum


class TestCreateProject:
    def setup_method(self):
        self.mock_project_repository = Mock(spec=ProjectRepository)
        self.mock_project_task_repository = Mock(spec=ProjectTaskRepository)
        self.create_project = CreateProject(
            self.mock_project_repository,
            self.mock_project_task_repository,
        )

    def test_create_project_basic(self):
        # Arrange
        mock_project = InsertedProject(
            id="test-id-123",
            name="新規プロジェクト",
            start_date=date(2024, 1, 1),
        )
        self.mock_project_repository.save.return_value = mock_project

        request = CreateProjectRequest(
            name="新規プロジェクト",
            start_date=date(2024, 1, 1),
        )

        # Act
        self.create_project.execute(request)

        # Assert
        self.mock_project_repository.save.assert_called_once()
        saved_project_arg = self.mock_project_repository.save.call_args[0][0]
        assert saved_project_arg.name == "新規プロジェクト"
        assert saved_project_arg.start_date == date(2024, 1, 1)
        assert saved_project_arg.end_date is None

    def test_create_project_with_end_date(self):
        # Arrange
        mock_project = InsertedProject(
            id="test-id-456",
            name="期限付きプロジェクト",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 3, 31),
        )
        self.mock_project_repository.save.return_value = mock_project

        request = CreateProjectRequest(
            name="期限付きプロジェクト",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 3, 31),
        )

        # Act
        self.create_project.execute(request)

        # Assert
        self.mock_project_repository.save.assert_called_once()
        saved_project_arg = self.mock_project_repository.save.call_args[0][0]
        assert saved_project_arg.name == "期限付きプロジェクト"
        assert saved_project_arg.start_date == date(2024, 1, 1)
        assert saved_project_arg.end_date == date(2024, 3, 31)

    def test_create_project_calls_repository_save(self):
        # Arrange
        mock_project = InsertedProject(
            id="test-id-789",
            name="テストプロジェクト",
            start_date=date(2024, 6, 1),
        )
        self.mock_project_repository.save.return_value = mock_project

        request = CreateProjectRequest(
            name="テストプロジェクト",
            start_date=date(2024, 6, 1),
        )

        # Act
        self.create_project.execute(request)

        # Assert
        self.mock_project_repository.save.assert_called_once()
        assert isinstance(self.mock_project_repository.save.call_args[0][0], Project)

    def test_create_project_also_creates_project_task(self):
        # Arrange
        project_name = "新規プロジェクト"
        project_id = "test-project-id"
        mock_project = InsertedProject(
            id=project_id,
            name=project_name,
            start_date=date(2024, 1, 1),
        )
        self.mock_project_repository.save.return_value = mock_project

        request = CreateProjectRequest(
            name=project_name,
            start_date=date(2024, 1, 1),
        )

        # Act
        self.create_project.execute(request)

        # Assert
        self.mock_project_task_repository.save.assert_called_once()
        saved_task_arg = self.mock_project_task_repository.save.call_args[0][0]
        assert isinstance(saved_task_arg, ProjectTask)
        assert saved_task_arg.title == project_name
        assert saved_task_arg.project_id == project_id
        assert saved_task_arg.status == ToDoStatusEnum.TODO

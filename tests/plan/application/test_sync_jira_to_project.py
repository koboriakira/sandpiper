from datetime import date
from unittest.mock import Mock

import pytest

from sandpiper.plan.application.sync_jira_to_project import SyncJiraToProject
from sandpiper.plan.domain.project import InsertedProject, Project
from sandpiper.plan.domain.project_task import InsertedProjectTask, ProjectTask
from sandpiper.plan.query.jira_ticket_dto import JiraTicketDto
from sandpiper.shared.valueobject.todo_status_enum import ToDoStatusEnum


class TestSyncJiraToProject:
    @pytest.fixture
    def mock_jira_ticket_query(self):
        return Mock()

    @pytest.fixture
    def mock_project_repository(self):
        return Mock()

    @pytest.fixture
    def mock_project_task_repository(self):
        return Mock()

    @pytest.fixture
    def sync_jira_to_project(self, mock_jira_ticket_query, mock_project_repository, mock_project_task_repository):
        return SyncJiraToProject(
            jira_ticket_query=mock_jira_ticket_query,
            project_repository=mock_project_repository,
            project_task_repository=mock_project_task_repository,
        )

    def test_execute_creates_project_and_task_for_new_ticket(
        self, sync_jira_to_project, mock_jira_ticket_query, mock_project_repository, mock_project_task_repository
    ):
        # Arrange
        ticket = JiraTicketDto(
            issue_key="SU-123",
            summary="Implement new feature",
            issue_type="Task",
            status="To Do",
            url="https://jira.example.com/browse/SU-123",
        )
        mock_jira_ticket_query.search_tickets.return_value = [ticket]
        mock_project_repository.find_by_jira_url.return_value = None  # No existing project

        inserted_project = InsertedProject(
            id="project-id-123",
            name="Implement new feature",
            start_date=date.today(),
            jira_url="https://jira.example.com/browse/SU-123",
        )
        mock_project_repository.save.return_value = inserted_project

        inserted_task = InsertedProjectTask(
            id="task-id-123",
            title="Implement new feature",
            status=ToDoStatusEnum.TODO,
            project_id="project-id-123",
        )
        mock_project_task_repository.save.return_value = inserted_task

        # Act
        result = sync_jira_to_project.execute(jira_project="SU")

        # Assert
        assert len(result.created_projects) == 1
        assert len(result.skipped_tickets) == 0
        assert result.created_projects[0].id == "project-id-123"
        assert result.created_projects[0].name == "Implement new feature"
        assert result.created_projects[0].jira_url == "https://jira.example.com/browse/SU-123"

        # Verify search_tickets called with correct parameters
        mock_jira_ticket_query.search_tickets.assert_called_once_with(
            project="SU",
            issue_type="Task,Story,Bug",
            status="To Do,In Progress",
            assignee="currentUser()",
            max_results=100,
        )

        # Verify project was saved
        saved_project: Project = mock_project_repository.save.call_args[0][0]
        assert saved_project.name == "Implement new feature"
        assert saved_project.jira_url == "https://jira.example.com/browse/SU-123"

        # Verify project task was created
        saved_task: ProjectTask = mock_project_task_repository.save.call_args[0][0]
        assert saved_task.title == "Implement new feature"
        assert saved_task.status == ToDoStatusEnum.TODO
        assert saved_task.project_id == "project-id-123"

    def test_execute_skips_ticket_with_existing_jira_url(
        self, sync_jira_to_project, mock_jira_ticket_query, mock_project_repository, mock_project_task_repository
    ):
        # Arrange
        ticket = JiraTicketDto(
            issue_key="SU-456",
            summary="Existing feature",
            issue_type="Story",
            status="In Progress",
            url="https://jira.example.com/browse/SU-456",
        )
        mock_jira_ticket_query.search_tickets.return_value = [ticket]

        # Project with same URL already exists
        existing_project = InsertedProject(
            id="existing-project-id",
            name="Existing feature",
            start_date=date.today(),
            jira_url="https://jira.example.com/browse/SU-456",
        )
        mock_project_repository.find_by_jira_url.return_value = existing_project

        # Act
        result = sync_jira_to_project.execute(jira_project="SU")

        # Assert
        assert len(result.created_projects) == 0
        assert len(result.skipped_tickets) == 1
        assert result.skipped_tickets[0].issue_key == "SU-456"

        # Verify project was NOT saved
        mock_project_repository.save.assert_not_called()
        mock_project_task_repository.save.assert_not_called()

    def test_execute_handles_mixed_new_and_existing_tickets(
        self, sync_jira_to_project, mock_jira_ticket_query, mock_project_repository, mock_project_task_repository
    ):
        # Arrange
        new_ticket = JiraTicketDto(
            issue_key="SU-100",
            summary="New feature",
            issue_type="Task",
            status="To Do",
            url="https://jira.example.com/browse/SU-100",
        )
        existing_ticket = JiraTicketDto(
            issue_key="SU-200",
            summary="Existing feature",
            issue_type="Bug",
            status="In Progress",
            url="https://jira.example.com/browse/SU-200",
        )
        mock_jira_ticket_query.search_tickets.return_value = [new_ticket, existing_ticket]

        # Mocking find_by_jira_url
        def find_by_jira_url(url):
            if url == "https://jira.example.com/browse/SU-200":
                return InsertedProject(
                    id="existing-id",
                    name="Existing feature",
                    start_date=date.today(),
                    jira_url=url,
                )
            return None

        mock_project_repository.find_by_jira_url.side_effect = find_by_jira_url

        inserted_project = InsertedProject(
            id="new-project-id",
            name="New feature",
            start_date=date.today(),
            jira_url="https://jira.example.com/browse/SU-100",
        )
        mock_project_repository.save.return_value = inserted_project

        inserted_task = InsertedProjectTask(
            id="new-task-id",
            title="New feature",
            status=ToDoStatusEnum.TODO,
            project_id="new-project-id",
        )
        mock_project_task_repository.save.return_value = inserted_task

        # Act
        result = sync_jira_to_project.execute(jira_project="SU")

        # Assert
        assert len(result.created_projects) == 1
        assert len(result.skipped_tickets) == 1
        assert result.created_projects[0].name == "New feature"
        assert result.skipped_tickets[0].issue_key == "SU-200"

    def test_execute_with_no_tickets(
        self, sync_jira_to_project, mock_jira_ticket_query, mock_project_repository, mock_project_task_repository
    ):
        # Arrange
        mock_jira_ticket_query.search_tickets.return_value = []

        # Act
        result = sync_jira_to_project.execute(jira_project="SU")

        # Assert
        assert len(result.created_projects) == 0
        assert len(result.skipped_tickets) == 0
        mock_project_repository.save.assert_not_called()
        mock_project_task_repository.save.assert_not_called()

    def test_execute_with_different_project(
        self,
        sync_jira_to_project,
        mock_jira_ticket_query,
        mock_project_repository,  # noqa: ARG002
        mock_project_task_repository,  # noqa: ARG002
    ):
        # Arrange
        mock_jira_ticket_query.search_tickets.return_value = []

        # Act
        sync_jira_to_project.execute(jira_project="OTHER")

        # Assert
        mock_jira_ticket_query.search_tickets.assert_called_once_with(
            project="OTHER",
            issue_type="Task,Story,Bug",
            status="To Do,In Progress",
            assignee="currentUser()",
            max_results=100,
        )

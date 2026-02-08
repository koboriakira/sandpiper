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
            status="In Progress",
            url="https://jira.example.com/browse/SU-123",
        )
        mock_jira_ticket_query.search_tickets.return_value = [ticket]
        mock_project_repository.fetch_projects_with_jira_url.return_value = []  # No existing projects

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
        assert len(result.notion_only_projects) == 0
        assert result.created_projects[0].id == "project-id-123"
        assert result.created_projects[0].name == "Implement new feature"
        assert result.created_projects[0].jira_url == "https://jira.example.com/browse/SU-123"

        # Verify search_tickets called with correct parameters
        mock_jira_ticket_query.search_tickets.assert_called_once_with(
            project="SU",
            issue_type="Task,Story,Bug",
            status="In Progress",
            assignee="currentUser()",
            max_results=100,
        )

        # Verify fetch_projects_with_jira_url was called once (API optimization)
        mock_project_repository.fetch_projects_with_jira_url.assert_called_once()

        # Verify project was saved with IN_PROGRESS status
        saved_project: Project = mock_project_repository.save.call_args[0][0]
        assert saved_project.name == "Implement new feature"
        assert saved_project.jira_url == "https://jira.example.com/browse/SU-123"
        assert saved_project.status == ToDoStatusEnum.IN_PROGRESS

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

        # URL already exists in the project database
        existing_project = InsertedProject(
            id="existing-project-id",
            name="Existing feature",
            start_date=date.today(),
            jira_url="https://jira.example.com/browse/SU-456",
        )
        mock_project_repository.fetch_projects_with_jira_url.return_value = [existing_project]

        # Act
        result = sync_jira_to_project.execute(jira_project="SU")

        # Assert
        assert len(result.created_projects) == 0
        assert len(result.skipped_tickets) == 1
        assert len(result.notion_only_projects) == 0
        assert result.skipped_tickets[0].issue_key == "SU-456"

        # Verify fetch_projects_with_jira_url was called once
        mock_project_repository.fetch_projects_with_jira_url.assert_called_once()

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
            status="In Progress",
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

        # Only SU-200 exists
        existing_project = InsertedProject(
            id="existing-project-id",
            name="Existing feature",
            start_date=date.today(),
            jira_url="https://jira.example.com/browse/SU-200",
        )
        mock_project_repository.fetch_projects_with_jira_url.return_value = [existing_project]

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
        assert len(result.notion_only_projects) == 0
        assert result.created_projects[0].name == "New feature"
        assert result.skipped_tickets[0].issue_key == "SU-200"

        # Verify fetch_projects_with_jira_url was called once (not per ticket)
        mock_project_repository.fetch_projects_with_jira_url.assert_called_once()

    def test_execute_with_no_tickets(
        self, sync_jira_to_project, mock_jira_ticket_query, mock_project_repository, mock_project_task_repository
    ):
        # Arrange
        mock_jira_ticket_query.search_tickets.return_value = []
        mock_project_repository.fetch_projects_with_jira_url.return_value = []

        # Act
        result = sync_jira_to_project.execute(jira_project="SU")

        # Assert
        assert len(result.created_projects) == 0
        assert len(result.skipped_tickets) == 0
        assert len(result.notion_only_projects) == 0
        mock_project_repository.save.assert_not_called()
        mock_project_task_repository.save.assert_not_called()

    def test_execute_with_different_project(
        self,
        sync_jira_to_project,
        mock_jira_ticket_query,
        mock_project_repository,
        mock_project_task_repository,  # noqa: ARG002
    ):
        # Arrange
        mock_jira_ticket_query.search_tickets.return_value = []
        mock_project_repository.fetch_projects_with_jira_url.return_value = []

        # Act
        sync_jira_to_project.execute(jira_project="OTHER")

        # Assert
        mock_jira_ticket_query.search_tickets.assert_called_once_with(
            project="OTHER",
            issue_type="Task,Story,Bug",
            status="In Progress",
            assignee="currentUser()",
            max_results=100,
        )

    def test_execute_prevents_duplicate_within_same_batch(
        self, sync_jira_to_project, mock_jira_ticket_query, mock_project_repository, mock_project_task_repository
    ):
        """同一バッチ内で同じURLのチケットが複数ある場合、最初の1つだけを作成する"""
        # Arrange
        ticket1 = JiraTicketDto(
            issue_key="SU-300",
            summary="Feature A",
            issue_type="Task",
            status="In Progress",
            url="https://jira.example.com/browse/SU-300",
        )
        ticket2 = JiraTicketDto(
            issue_key="SU-301",
            summary="Feature A duplicate",
            issue_type="Task",
            status="In Progress",
            url="https://jira.example.com/browse/SU-300",  # Same URL as ticket1
        )
        mock_jira_ticket_query.search_tickets.return_value = [ticket1, ticket2]
        mock_project_repository.fetch_projects_with_jira_url.return_value = []

        inserted_project = InsertedProject(
            id="project-id-300",
            name="Feature A",
            start_date=date.today(),
            jira_url="https://jira.example.com/browse/SU-300",
        )
        mock_project_repository.save.return_value = inserted_project

        inserted_task = InsertedProjectTask(
            id="task-id-300",
            title="Feature A",
            status=ToDoStatusEnum.TODO,
            project_id="project-id-300",
        )
        mock_project_task_repository.save.return_value = inserted_task

        # Act
        result = sync_jira_to_project.execute(jira_project="SU")

        # Assert
        assert len(result.created_projects) == 1
        assert len(result.skipped_tickets) == 1
        assert len(result.notion_only_projects) == 0
        assert result.created_projects[0].name == "Feature A"
        assert result.skipped_tickets[0].issue_key == "SU-301"  # Second ticket was skipped

        # Verify save was called only once
        assert mock_project_repository.save.call_count == 1
        assert mock_project_task_repository.save.call_count == 1

    def test_execute_detects_notion_only_projects(
        self,
        sync_jira_to_project,
        mock_jira_ticket_query,
        mock_project_repository,
        mock_project_task_repository,  # noqa: ARG002
    ):
        """JIRA側に存在しないNotionプロジェクトをnotion_only_projectsとして検出する"""
        # Arrange
        # JIRAにはSU-500のみ存在
        ticket = JiraTicketDto(
            issue_key="SU-500",
            summary="Active feature",
            issue_type="Task",
            status="In Progress",
            url="https://jira.example.com/browse/SU-500",
        )
        mock_jira_ticket_query.search_tickets.return_value = [ticket]

        # NotionにはSU-500とSU-999の両方が存在(SU-999はJIRA側で完了済み)
        active_project = InsertedProject(
            id="active-project-id",
            name="Active feature",
            start_date=date.today(),
            jira_url="https://jira.example.com/browse/SU-500",
        )
        completed_project = InsertedProject(
            id="completed-project-id",
            name="Completed feature",
            start_date=date.today(),
            jira_url="https://jira.example.com/browse/SU-999",
        )
        mock_project_repository.fetch_projects_with_jira_url.return_value = [active_project, completed_project]

        # Act
        result = sync_jira_to_project.execute(jira_project="SU")

        # Assert
        assert len(result.created_projects) == 0
        assert len(result.skipped_tickets) == 1  # SU-500 is skipped (already exists)
        assert len(result.notion_only_projects) == 1
        assert result.notion_only_projects[0].id == "completed-project-id"
        assert result.notion_only_projects[0].name == "Completed feature"
        assert result.notion_only_projects[0].jira_url == "https://jira.example.com/browse/SU-999"

    def test_execute_notion_only_filters_by_jira_project(
        self,
        sync_jira_to_project,
        mock_jira_ticket_query,
        mock_project_repository,
        mock_project_task_repository,  # noqa: ARG002
    ):
        """notion_only_projectsは対象JIRAプロジェクトのものだけをフィルタリングする"""
        # Arrange
        mock_jira_ticket_query.search_tickets.return_value = []  # JIRAにはチケットなし

        # Notionには別プロジェクト(OTHER)のURLを持つプロジェクトが存在
        other_project = InsertedProject(
            id="other-project-id",
            name="Other project feature",
            start_date=date.today(),
            jira_url="https://jira.example.com/browse/OTHER-123",  # 別プロジェクト
        )
        su_project = InsertedProject(
            id="su-project-id",
            name="SU project feature",
            start_date=date.today(),
            jira_url="https://jira.example.com/browse/SU-888",  # 対象プロジェクト
        )
        mock_project_repository.fetch_projects_with_jira_url.return_value = [other_project, su_project]

        # Act
        result = sync_jira_to_project.execute(jira_project="SU")

        # Assert
        # OTHER-123は対象外なので含まれない、SU-888のみがnotion_only_projectsに含まれる
        assert len(result.notion_only_projects) == 1
        assert result.notion_only_projects[0].id == "su-project-id"
        assert result.notion_only_projects[0].jira_url == "https://jira.example.com/browse/SU-888"

    def test_execute_excludes_done_projects_from_notion_only(
        self,
        sync_jira_to_project,
        mock_jira_ticket_query,
        mock_project_repository,
        mock_project_task_repository,  # noqa: ARG002
    ):
        """Doneステータスのプロジェクトはnotion_only_projectsに含めない"""
        # Arrange
        mock_jira_ticket_query.search_tickets.return_value = []  # JIRAにはチケットなし

        # Notionには3つのプロジェクトが存在:
        # - SU-111: IN_PROGRESS → notion_only_projectsに含まれるべき
        # - SU-222: Done → notion_only_projectsに含めない
        # - SU-333: ステータスなし → notion_only_projectsに含まれるべき
        in_progress_project = InsertedProject(
            id="in-progress-project-id",
            name="In progress feature",
            start_date=date.today(),
            jira_url="https://jira.example.com/browse/SU-111",
            status=ToDoStatusEnum.IN_PROGRESS,
        )
        done_project = InsertedProject(
            id="done-project-id",
            name="Done feature",
            start_date=date.today(),
            jira_url="https://jira.example.com/browse/SU-222",
            status=ToDoStatusEnum.DONE,
        )
        no_status_project = InsertedProject(
            id="no-status-project-id",
            name="No status feature",
            start_date=date.today(),
            jira_url="https://jira.example.com/browse/SU-333",
        )
        mock_project_repository.fetch_projects_with_jira_url.return_value = [
            in_progress_project,
            done_project,
            no_status_project,
        ]

        # Act
        result = sync_jira_to_project.execute(jira_project="SU")

        # Assert
        assert len(result.notion_only_projects) == 2
        notion_only_ids = {p.id for p in result.notion_only_projects}
        assert "in-progress-project-id" in notion_only_ids
        assert "no-status-project-id" in notion_only_ids
        assert "done-project-id" not in notion_only_ids

    def test_execute_no_notion_only_when_all_match(
        self,
        sync_jira_to_project,
        mock_jira_ticket_query,
        mock_project_repository,
        mock_project_task_repository,  # noqa: ARG002
    ):
        """JIRAとNotionのプロジェクトがすべて一致する場合はnotion_only_projectsは空"""
        # Arrange
        ticket = JiraTicketDto(
            issue_key="SU-600",
            summary="Matching feature",
            issue_type="Task",
            status="In Progress",
            url="https://jira.example.com/browse/SU-600",
        )
        mock_jira_ticket_query.search_tickets.return_value = [ticket]

        matching_project = InsertedProject(
            id="matching-project-id",
            name="Matching feature",
            start_date=date.today(),
            jira_url="https://jira.example.com/browse/SU-600",
        )
        mock_project_repository.fetch_projects_with_jira_url.return_value = [matching_project]

        # Act
        result = sync_jira_to_project.execute(jira_project="SU")

        # Assert
        assert len(result.created_projects) == 0
        assert len(result.skipped_tickets) == 1
        assert len(result.notion_only_projects) == 0

from datetime import UTC, datetime
from unittest.mock import Mock, patch

import pytest

from sandpiper.plan.query.jira_ticket_dto import JiraTicketDto
from sandpiper.plan.query.jira_ticket_query import RestApiJiraTicketQuery


class TestRestApiJiraTicketQuery:
    @pytest.fixture
    def mock_session(self):
        with patch("sandpiper.plan.query.jira_ticket_query.Session") as mock_session_class:
            mock_session_instance = Mock()
            mock_session_class.return_value = mock_session_instance
            yield mock_session_instance

    @pytest.fixture
    def jira_query(self, mock_session):  # noqa: ARG002
        with patch.dict(
            "os.environ",
            {
                "BUSINESS_JIRA_BASE_URL": "https://jira.atlassian.com",
                "BUSINESS_JIRA_USERNAME": "test@example.com",
                "BUSINESS_JIRA_API_TOKEN": "test-token",
            },
        ):
            return RestApiJiraTicketQuery()

    def test_init_with_env_variables(self, mock_session):
        with patch.dict(
            "os.environ",
            {
                "BUSINESS_JIRA_BASE_URL": "https://example.atlassian.net",
                "BUSINESS_JIRA_USERNAME": "test@example.com",
                "BUSINESS_JIRA_API_TOKEN": "test-token",
            },
        ):
            query = RestApiJiraTicketQuery()

            assert query.base_url == "https://example.atlassian.net"
            assert query.session.auth == ("test@example.com", "test-token")
            mock_session.headers.update.assert_called_with({"Accept": "application/json"})

    def test_init_without_credentials_raises_error(self):
        with (
            patch.dict("os.environ", {}, clear=True),
            pytest.raises(ValueError, match="BUSINESS_JIRA_USERNAME and BUSINESS_JIRA_API_TOKEN must be set"),
        ):
            RestApiJiraTicketQuery()

    def test_search_tickets_with_jql(self, jira_query):
        # Setup mock response
        mock_response = Mock()
        mock_response.json.return_value = {
            "issues": [
                {
                    "key": "TEST-123",
                    "fields": {
                        "summary": "Test Issue",
                        "issuetype": {"name": "Bug"},
                        "status": {"name": "Open"},
                        "priority": {"name": "High"},
                        "assignee": {"displayName": "John Doe"},
                        "reporter": {"displayName": "Jane Smith"},
                        "created": "2024-01-01T10:00:00.000+0000",
                        "updated": "2024-01-02T15:00:00.000+0000",
                        "duedate": "2024-01-10T00:00:00.000+0000",
                        "description": "Test description",
                        "labels": ["bug", "urgent"],
                        "fixVersions": [{"name": "v1.0"}],
                        "components": [{"name": "Backend"}],
                        "customfield_10020": [{"name": "Sprint 1"}],
                        "customfield_10016": 5,
                        "customfield_10014": "EPIC-100",
                        "parent": {"key": "STORY-50"},
                        "customfield_10328": "#123",
                    },
                }
            ],
            "total": 1,
        }
        jira_query.session.get.return_value = mock_response

        # Execute
        tickets = jira_query.search_tickets(jql='project = "TEST"', max_results=10)

        # Assert
        assert len(tickets) == 1
        ticket = tickets[0]
        assert ticket.issue_key == "TEST-123"
        assert ticket.summary == "Test Issue"
        assert ticket.issue_type == "Bug"
        assert ticket.status == "Open"
        assert ticket.priority == "High"
        assert ticket.assignee == "John Doe"
        assert ticket.reporter == "Jane Smith"
        assert ticket.created == datetime(2024, 1, 1, 10, 0, 0, tzinfo=UTC)
        assert ticket.updated == datetime(2024, 1, 2, 15, 0, 0, tzinfo=UTC)
        assert ticket.due_date == datetime(2024, 1, 10, 0, 0, 0, tzinfo=UTC)
        assert ticket.description == "Test description"
        assert ticket.labels == ["bug", "urgent"]
        assert ticket.fix_versions == ["v1.0"]
        assert ticket.components == ["Backend"]
        assert ticket.sprint == "Sprint 1"
        assert ticket.story_points == 5
        assert ticket.epic_key == "EPIC-100"
        assert ticket.parent_key == "STORY-50"
        assert ticket.github_issue == "#123"
        assert ticket.url == "https://jira.atlassian.com/browse/TEST-123"

    def test_search_tickets_with_filters(self, jira_query):
        mock_response = Mock()
        mock_response.json.return_value = {"issues": [], "total": 0}
        jira_query.session.get.return_value = mock_response

        # Execute
        jira_query.search_tickets(
            project="TEST",
            issue_type="Bug,Task",
            status="Open,In Progress",
            assignee="currentUser()",
        )

        # Check JQL construction
        call_args = jira_query.session.get.call_args
        params = call_args[1]["params"]
        expected_jql = 'project = "TEST" AND issuetype IN ("Bug","Task") AND status IN ("Open","In Progress") AND assignee = currentUser() ORDER BY created DESC'
        assert params["jql"] == expected_jql

    def test_get_ticket_found(self, jira_query):
        # Setup mock response
        mock_response = Mock()
        mock_response.json.return_value = {
            "key": "TEST-456",
            "fields": {
                "summary": "Single Issue",
                "issuetype": {"name": "Story"},
                "status": {"name": "Done"},
            },
        }
        jira_query.session.get.return_value = mock_response

        # Execute
        ticket = jira_query.get_ticket("TEST-456")

        # Assert
        assert ticket is not None
        assert ticket.issue_key == "TEST-456"
        assert ticket.summary == "Single Issue"
        assert ticket.issue_type == "Story"
        assert ticket.status == "Done"

        # Check API call
        jira_query.session.get.assert_called_once_with("https://jira.atlassian.com/rest/api/3/issue/TEST-456")

    def test_get_ticket_not_found(self, jira_query):
        # Setup 404 response
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = pytest.importorskip("requests").HTTPError(response=mock_response)
        jira_query.session.get.return_value = mock_response

        # Execute
        ticket = jira_query.get_ticket("NOTFOUND-999")

        # Assert
        assert ticket is None

    def test_parse_datetime_various_formats(self, jira_query):
        # Test ISO format with timezone
        result = jira_query._parse_datetime("2024-01-15T10:30:45.000+0000")
        assert result == datetime(2024, 1, 15, 10, 30, 45, tzinfo=UTC)

        # Test Z timezone
        result = jira_query._parse_datetime("2024-01-15T10:30:45.000Z")
        assert result == datetime(2024, 1, 15, 10, 30, 45, tzinfo=UTC)

        # Test None
        result = jira_query._parse_datetime(None)
        assert result is None

        # Test invalid format
        result = jira_query._parse_datetime("invalid-date")
        assert result is None

    def test_build_jql_empty(self, jira_query):
        jql = jira_query._build_jql()
        assert jql == "ORDER BY created DESC"

    def test_build_jql_with_single_values(self, jira_query):
        jql = jira_query._build_jql(
            project="PROJ",
            issue_type="Bug",
            status="Open",
            assignee="john.doe",
        )
        expected = (
            'project = "PROJ" AND issuetype = "Bug" AND status = "Open" AND assignee = "john.doe" ORDER BY created DESC'
        )
        assert jql == expected

    def test_build_jql_with_multiple_values(self, jira_query):
        jql = jira_query._build_jql(
            issue_type="Bug, Task, Story",
            status="Open, In Progress",
        )
        expected = 'issuetype IN ("Bug","Task","Story") AND status IN ("Open","In Progress") ORDER BY created DESC'
        assert jql == expected

    def test_build_jql_with_current_user(self, jira_query):
        jql = jira_query._build_jql(assignee="currentUser()")
        assert jql == "assignee = currentUser() ORDER BY created DESC"

    def test_pagination(self, jira_query):
        # Setup paginated responses
        call_count = 0

        def mock_get(url, params=None):  # noqa: ARG001
            nonlocal call_count
            mock_response = Mock()

            if call_count == 0:
                # First call - return 100 issues
                mock_response.json.return_value = {
                    "issues": [
                        {
                            "key": f"TEST-{i}",
                            "fields": {
                                "summary": f"Issue {i}",
                                "issuetype": {"name": "Task"},
                                "status": {"name": "Open"},
                            },
                        }
                        for i in range(1, 101)
                    ],
                    "total": 150,
                }
                # Verify first call has startAt=0
                assert params["startAt"] == 0
            else:
                # Second call - return 20 issues
                mock_response.json.return_value = {
                    "issues": [
                        {
                            "key": f"TEST-{i}",
                            "fields": {
                                "summary": f"Issue {i}",
                                "issuetype": {"name": "Task"},
                                "status": {"name": "Open"},
                            },
                        }
                        for i in range(101, 121)
                    ],
                    "total": 150,
                }
                # Verify second call has startAt=100
                assert params["startAt"] == 100

            mock_response.raise_for_status.return_value = None
            call_count += 1
            return mock_response

        # Mock the session.get method
        jira_query.session.get = mock_get

        # Execute
        tickets = jira_query.search_tickets(max_results=120)

        # Assert
        assert len(tickets) == 120
        assert tickets[0].issue_key == "TEST-1"
        assert tickets[99].issue_key == "TEST-100"
        assert tickets[119].issue_key == "TEST-120"
        assert call_count == 2


class TestJiraTicketDto:
    def test_to_dict(self):
        ticket = JiraTicketDto(
            issue_key="TEST-123",
            summary="Test Issue",
            issue_type="Bug",
            status="Open",
            priority="High",
            assignee="John Doe",
            reporter="Jane Smith",
            created=datetime(2024, 1, 1, 10, 0, 0),
            updated=datetime(2024, 1, 2, 15, 0, 0),
            due_date=datetime(2024, 1, 10, 0, 0, 0),
            description="Test description",
            labels=["bug", "urgent"],
            fix_versions=["v1.0"],
            components=["Backend"],
            sprint="Sprint 1",
            story_points=5.0,
            epic_key="EPIC-100",
            parent_key="STORY-50",
            github_issue="#123",
            url="https://jira.atlassian.com/browse/TEST-123",
        )

        result = ticket.to_dict()

        assert result == {
            "issue_key": "TEST-123",
            "summary": "Test Issue",
            "issue_type": "Bug",
            "status": "Open",
            "priority": "High",
            "assignee": "John Doe",
            "reporter": "Jane Smith",
            "created": "2024-01-01T10:00:00",
            "updated": "2024-01-02T15:00:00",
            "due_date": "2024-01-10T00:00:00",
            "description": "Test description",
            "labels": ["bug", "urgent"],
            "fix_versions": ["v1.0"],
            "components": ["Backend"],
            "sprint": "Sprint 1",
            "story_points": 5.0,
            "epic_key": "EPIC-100",
            "parent_key": "STORY-50",
            "github_issue": "#123",
            "url": "https://jira.atlassian.com/browse/TEST-123",
        }

    def test_to_dict_with_none_values(self):
        ticket = JiraTicketDto(
            issue_key="TEST-456",
            summary="Minimal Issue",
            issue_type="Task",
            status="Open",
        )

        result = ticket.to_dict()

        assert result["issue_key"] == "TEST-456"
        assert result["summary"] == "Minimal Issue"
        assert result["issue_type"] == "Task"
        assert result["status"] == "Open"
        assert result["priority"] is None
        assert result["created"] is None
        assert result["labels"] is None

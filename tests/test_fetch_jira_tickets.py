"""fetch-jira-tickets コマンドのテスト"""

import json
import sys
from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from sandpiper.plan.query.jira_ticket_dto import JiraTicketDto


def _get_runner_and_app():
    modules_to_remove = [key for key in sys.modules if key.startswith("sandpiper")]
    for module in modules_to_remove:
        del sys.modules[module]

    with (
        patch.dict("os.environ", {"GITHUB_TOKEN": "t", "NOTION_SECRET": "t"}),
        patch("sandpiper.app.app.bootstrap") as mock_bootstrap,
    ):
        mock_bootstrap.return_value = MagicMock()
        from sandpiper.main import app

        return CliRunner(), app


def _make_ticket(issue_key: str = "TEST-1") -> JiraTicketDto:
    return JiraTicketDto(
        issue_key=issue_key,
        summary="テストチケット",
        issue_type="Bug",
        status="Open",
    )


class TestFetchJiraTickets:
    def setup_method(self):
        self.runner, self.app = _get_runner_and_app()

    def test_outputs_json_to_stdout(self):
        with (
            patch.dict(
                "os.environ",
                {
                    "BUSINESS_JIRA_USERNAME": "user@example.com",
                    "BUSINESS_JIRA_API_TOKEN": "token",
                },
            ),
            patch("sandpiper.plan.query.jira_ticket_query.RestApiJiraTicketQuery") as MockQuery,
        ):
            instance = MockQuery.return_value
            instance.search_tickets.return_value = [_make_ticket("PROJ-1")]

            result = self.runner.invoke(self.app, ["fetch-jira-tickets"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert isinstance(data, list)
        assert data[0]["issue_key"] == "PROJ-1"

    def test_uses_project_option(self):
        with (
            patch.dict(
                "os.environ",
                {
                    "BUSINESS_JIRA_USERNAME": "user@example.com",
                    "BUSINESS_JIRA_API_TOKEN": "token",
                },
            ),
            patch("sandpiper.plan.query.jira_ticket_query.RestApiJiraTicketQuery") as MockQuery,
        ):
            instance = MockQuery.return_value
            instance.search_tickets.return_value = []

            result = self.runner.invoke(self.app, ["fetch-jira-tickets", "--project", "MYPROJ"])

        assert result.exit_code == 0
        instance.search_tickets.assert_called_once_with(
            jql=None,
            project="MYPROJ",
            status=None,
            max_results=50,
        )

    def test_uses_business_jira_project_env_as_default(self):
        with (
            patch.dict(
                "os.environ",
                {
                    "BUSINESS_JIRA_USERNAME": "user@example.com",
                    "BUSINESS_JIRA_API_TOKEN": "token",
                    "BUSINESS_JIRA_PROJECT": "ENVPROJ",
                },
            ),
            patch("sandpiper.plan.query.jira_ticket_query.RestApiJiraTicketQuery") as MockQuery,
        ):
            instance = MockQuery.return_value
            instance.search_tickets.return_value = []

            result = self.runner.invoke(self.app, ["fetch-jira-tickets"])

        assert result.exit_code == 0
        instance.search_tickets.assert_called_once_with(
            jql=None,
            project="ENVPROJ",
            status=None,
            max_results=50,
        )

    def test_uses_status_option(self):
        with (
            patch.dict(
                "os.environ",
                {
                    "BUSINESS_JIRA_USERNAME": "user@example.com",
                    "BUSINESS_JIRA_API_TOKEN": "token",
                },
            ),
            patch("sandpiper.plan.query.jira_ticket_query.RestApiJiraTicketQuery") as MockQuery,
        ):
            instance = MockQuery.return_value
            instance.search_tickets.return_value = []

            result = self.runner.invoke(self.app, ["fetch-jira-tickets", "--status", "In Progress,Done"])

        assert result.exit_code == 0
        call_kwargs = instance.search_tickets.call_args.kwargs
        assert call_kwargs["status"] == "In Progress,Done"
        assert call_kwargs["jql"] is None
        assert call_kwargs["max_results"] == 50

    def test_uses_jql_option(self):
        with (
            patch.dict(
                "os.environ",
                {
                    "BUSINESS_JIRA_USERNAME": "user@example.com",
                    "BUSINESS_JIRA_API_TOKEN": "token",
                },
            ),
            patch("sandpiper.plan.query.jira_ticket_query.RestApiJiraTicketQuery") as MockQuery,
        ):
            instance = MockQuery.return_value
            instance.search_tickets.return_value = []

            result = self.runner.invoke(self.app, ["fetch-jira-tickets", "--jql", 'project = "TEST" AND status = "Open"'])

        assert result.exit_code == 0
        call_kwargs = instance.search_tickets.call_args.kwargs
        assert call_kwargs["jql"] == 'project = "TEST" AND status = "Open"'
        assert call_kwargs["status"] is None
        assert call_kwargs["max_results"] == 50

    def test_uses_max_results_option(self):
        with (
            patch.dict(
                "os.environ",
                {
                    "BUSINESS_JIRA_USERNAME": "user@example.com",
                    "BUSINESS_JIRA_API_TOKEN": "token",
                },
            ),
            patch("sandpiper.plan.query.jira_ticket_query.RestApiJiraTicketQuery") as MockQuery,
        ):
            instance = MockQuery.return_value
            instance.search_tickets.return_value = []

            result = self.runner.invoke(self.app, ["fetch-jira-tickets", "--max-results", "10"])

        assert result.exit_code == 0
        call_kwargs = instance.search_tickets.call_args.kwargs
        assert call_kwargs["max_results"] == 10

    def test_writes_to_file_when_output_specified(self, tmp_path):
        output_file = tmp_path / "tickets.json"
        with (
            patch.dict(
                "os.environ",
                {
                    "BUSINESS_JIRA_USERNAME": "user@example.com",
                    "BUSINESS_JIRA_API_TOKEN": "token",
                },
            ),
            patch("sandpiper.plan.query.jira_ticket_query.RestApiJiraTicketQuery") as MockQuery,
        ):
            instance = MockQuery.return_value
            instance.search_tickets.return_value = [_make_ticket("PROJ-2")]

            result = self.runner.invoke(self.app, ["fetch-jira-tickets", "--output", str(output_file)])

        assert result.exit_code == 0
        assert output_file.exists()
        data = json.loads(output_file.read_text(encoding="utf-8"))
        assert data[0]["issue_key"] == "PROJ-2"

    def test_exits_with_error_when_credentials_missing(self):
        with patch.dict(
            "os.environ",
            {"BUSINESS_JIRA_USERNAME": "", "BUSINESS_JIRA_API_TOKEN": ""},
            clear=False,
        ):
            result = self.runner.invoke(self.app, ["fetch-jira-tickets"])

        assert result.exit_code == 1

    def test_output_is_valid_json_with_ensure_ascii_false(self):
        with (
            patch.dict(
                "os.environ",
                {
                    "BUSINESS_JIRA_USERNAME": "user@example.com",
                    "BUSINESS_JIRA_API_TOKEN": "token",
                },
            ),
            patch("sandpiper.plan.query.jira_ticket_query.RestApiJiraTicketQuery") as MockQuery,
        ):
            ticket = JiraTicketDto(
                issue_key="PROJ-3",
                summary="日本語のサマリー",
                issue_type="Story",
                status="進行中",
            )
            instance = MockQuery.return_value
            instance.search_tickets.return_value = [ticket]

            result = self.runner.invoke(self.app, ["fetch-jira-tickets"])

        assert result.exit_code == 0
        # 日本語がエスケープされずそのまま含まれることを確認
        assert "日本語のサマリー" in result.output
        data = json.loads(result.output)
        assert data[0]["summary"] == "日本語のサマリー"

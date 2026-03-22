"""sandpiper jira get コマンドのテスト"""

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


def _make_ticket(issue_key: str = "SU-1234") -> JiraTicketDto:
    return JiraTicketDto(
        issue_key=issue_key,
        summary="テストチケット",
        issue_type="Bug",
        status="Open",
    )


class TestJiraGet:
    def setup_method(self):
        self.runner, self.app = _get_runner_and_app()

    def test_get_ticket_by_key_outputs_json(self):
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
            instance.get_ticket.return_value = _make_ticket("SU-1234")

            result = self.runner.invoke(self.app, ["jira", "get", "SU-1234"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["issue_key"] == "SU-1234"
        instance.get_ticket.assert_called_once_with("SU-1234")

    def test_get_ticket_by_url_extracts_key(self):
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
            instance.get_ticket.return_value = _make_ticket("SU-1234")

            result = self.runner.invoke(
                self.app,
                ["jira", "get", "https://mycompany.atlassian.net/browse/SU-1234"],
            )

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["issue_key"] == "SU-1234"
        instance.get_ticket.assert_called_once_with("SU-1234")

    def test_get_ticket_writes_to_file_when_output_specified(self, tmp_path):
        output_file = tmp_path / "ticket.json"
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
            instance.get_ticket.return_value = _make_ticket("SU-5678")

            result = self.runner.invoke(
                self.app,
                ["jira", "get", "SU-5678", "-o", str(output_file)],
            )

        assert result.exit_code == 0
        assert output_file.exists()
        data = json.loads(output_file.read_text(encoding="utf-8"))
        assert data["issue_key"] == "SU-5678"

    def test_get_ticket_not_found_exits_with_error(self):
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
            instance.get_ticket.return_value = None

            result = self.runner.invoke(self.app, ["jira", "get", "NOTFOUND-999"])

        assert result.exit_code == 1

    def test_get_ticket_exits_with_error_when_credentials_missing(self):
        with patch.dict(
            "os.environ",
            {"BUSINESS_JIRA_USERNAME": "", "BUSINESS_JIRA_API_TOKEN": ""},
            clear=False,
        ):
            result = self.runner.invoke(self.app, ["jira", "get", "SU-1234"])

        assert result.exit_code == 1

    def test_output_contains_japanese_without_escaping(self):
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
                issue_key="SU-100",
                summary="日本語のタイトル",
                issue_type="Story",
                status="進行中",
            )
            instance = MockQuery.return_value
            instance.get_ticket.return_value = ticket

            result = self.runner.invoke(self.app, ["jira", "get", "SU-100"])

        assert result.exit_code == 0
        assert "日本語のタイトル" in result.output
        data = json.loads(result.output)
        assert data["summary"] == "日本語のタイトル"

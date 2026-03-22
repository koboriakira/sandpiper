"""sandpiper jira search コマンドのテスト"""

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


def _make_ticket(issue_key: str = "SU-1", sprint: str | None = "Sprint 1") -> JiraTicketDto:
    return JiraTicketDto(
        issue_key=issue_key,
        summary="テストチケット",
        issue_type="Task",
        status="In Progress",
        sprint=sprint,
    )


class TestJiraSearch:
    def setup_method(self):
        self.runner, self.app = _get_runner_and_app()

    def test_default_search_uses_current_user_and_open_sprints(self):
        """デフォルト動作: currentUser のアクティブスプリント内 Epic/Task を検索"""
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
            instance.search_tickets.return_value = [_make_ticket("SU-1")]

            result = self.runner.invoke(self.app, ["jira", "search"])

        assert result.exit_code == 0
        call_kwargs = instance.search_tickets.call_args.kwargs
        assert "currentUser()" in call_kwargs["jql"]
        assert "openSprints()" in call_kwargs["jql"]
        assert "Epic" in call_kwargs["jql"]
        assert "Task" in call_kwargs["jql"]

    def test_table_output_contains_ticket_key(self):
        """table 出力にチケットキーが含まれる"""
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
            instance.search_tickets.return_value = [_make_ticket("SU-999")]

            result = self.runner.invoke(self.app, ["jira", "search"])

        assert result.exit_code == 0
        assert "SU-999" in result.output

    def test_json_output_format(self):
        """--output json で JSON 形式の出力"""
        import json

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
            instance.search_tickets.return_value = [_make_ticket("SU-42")]

            result = self.runner.invoke(self.app, ["jira", "search", "--output", "json"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert isinstance(data, list)
        assert data[0]["issue_key"] == "SU-42"

    def test_assignee_option(self):
        """--assignee オプションで担当者を指定"""
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

            result = self.runner.invoke(self.app, ["jira", "search", "--assignee", "john@example.com"])

        assert result.exit_code == 0
        call_kwargs = instance.search_tickets.call_args.kwargs
        assert "john@example.com" in call_kwargs["jql"]

    def test_type_option(self):
        """--type オプションで issueType を指定"""
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

            result = self.runner.invoke(self.app, ["jira", "search", "--type", "Bug"])

        assert result.exit_code == 0
        call_kwargs = instance.search_tickets.call_args.kwargs
        assert "Bug" in call_kwargs["jql"]

    def test_no_sprint_flag_removes_sprint_filter(self):
        """--no-sprint フラグでスプリント縛りを外す"""
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

            result = self.runner.invoke(self.app, ["jira", "search", "--no-sprint"])

        assert result.exit_code == 0
        call_kwargs = instance.search_tickets.call_args.kwargs
        assert "openSprints()" not in call_kwargs["jql"]

    def test_jql_option_overrides_other_filters(self):
        """--jql オプション指定時は他フィルタを無視して生 JQL を使用"""
        custom_jql = 'project = "MYPROJ" AND status = "Done"'
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

            result = self.runner.invoke(self.app, ["jira", "search", "--jql", custom_jql])

        assert result.exit_code == 0
        call_kwargs = instance.search_tickets.call_args.kwargs
        assert call_kwargs["jql"] == custom_jql

    def test_project_option(self):
        """--project オプションでプロジェクトを指定"""
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

            result = self.runner.invoke(self.app, ["jira", "search", "--project", "MYPROJ"])

        assert result.exit_code == 0
        call_kwargs = instance.search_tickets.call_args.kwargs
        assert "MYPROJ" in call_kwargs["jql"]

    def test_no_tickets_found_message(self):
        """チケットが見つからない場合のメッセージ"""
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

            result = self.runner.invoke(self.app, ["jira", "search"])

        assert result.exit_code == 0

    def test_exits_with_error_when_credentials_missing(self):
        """認証情報がない場合はエラーで終了"""
        with patch.dict(
            "os.environ",
            {"BUSINESS_JIRA_USERNAME": "", "BUSINESS_JIRA_API_TOKEN": ""},
            clear=False,
        ):
            result = self.runner.invoke(self.app, ["jira", "search"])

        assert result.exit_code == 1

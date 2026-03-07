"""project サブコマンドのテスト"""

import json
import sys
from datetime import date
from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from sandpiper.plan.domain.project import InsertedProject
from sandpiper.shared.valueobject.todo_status_enum import ToDoStatusEnum


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


def _make_project(page_id: str = "proj-1") -> InsertedProject:
    return InsertedProject(
        id=page_id,
        name="テストプロジェクト",
        start_date=date(2026, 1, 1),
        end_date=None,
        status=ToDoStatusEnum.TODO,
        jira_url=None,
        claude_url=None,
    )


class TestProjectGet:
    def setup_method(self):
        self.runner, self.app = _get_runner_and_app()

    def test_get_returns_json(self):
        with patch("sandpiper.plan.infrastructure.notion_project_repository.NotionProjectRepository") as MockRepo:
            instance = MockRepo.return_value
            instance.find_as_inserted.return_value = _make_project("proj-abc")

            result = self.runner.invoke(self.app, ["project", "get", "proj-abc"])

        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert data["id"] == "proj-abc"
        assert data["name"] == "テストプロジェクト"
        assert data["status"] == "ToDo"

    def test_get_shows_end_date_when_set(self):
        project = InsertedProject(
            id="proj-2",
            name="完了済みプロジェクト",
            start_date=date(2026, 1, 1),
            end_date=date(2026, 3, 1),
            status=ToDoStatusEnum.DONE,
            jira_url=None,
            claude_url=None,
        )
        with patch("sandpiper.plan.infrastructure.notion_project_repository.NotionProjectRepository") as MockRepo:
            instance = MockRepo.return_value
            instance.find_as_inserted.return_value = project

            result = self.runner.invoke(self.app, ["project", "get", "proj-2"])

        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert data["end_date"] == "2026-03-01"
        assert data["status"] == "Done"


class TestProjectList:
    def setup_method(self):
        self.runner, self.app = _get_runner_and_app()

    def test_list_returns_json_array(self):
        projects = [_make_project("p1"), _make_project("p2")]
        with patch("sandpiper.plan.infrastructure.notion_project_repository.NotionProjectRepository") as MockRepo:
            instance = MockRepo.return_value
            instance.fetch_all.return_value = projects

            result = self.runner.invoke(self.app, ["project", "list"])

        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert len(data) == 2

    def test_list_filters_by_status(self):
        p_todo = _make_project("p1")
        p_done = InsertedProject(id="p2", name="完了", start_date=date(2026, 1, 1), status=ToDoStatusEnum.DONE)
        with patch("sandpiper.plan.infrastructure.notion_project_repository.NotionProjectRepository") as MockRepo:
            instance = MockRepo.return_value
            instance.fetch_all.return_value = [p_todo, p_done]

            result = self.runner.invoke(self.app, ["project", "list", "--status", "DONE"])

        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert len(data) == 1
        assert data[0]["id"] == "p2"

    def test_list_invalid_status_exits_with_error(self):
        with patch("sandpiper.plan.infrastructure.notion_project_repository.NotionProjectRepository") as MockRepo:
            instance = MockRepo.return_value
            instance.fetch_all.return_value = []

            result = self.runner.invoke(self.app, ["project", "list", "--status", "INVALID"])

        assert result.exit_code == 1


class TestProjectUpdate:
    def setup_method(self):
        self.runner, self.app = _get_runner_and_app()

    def test_update_status(self):
        with patch("sandpiper.plan.infrastructure.notion_project_repository.NotionProjectRepository") as MockRepo:
            instance = MockRepo.return_value

            result = self.runner.invoke(self.app, ["project", "update", "proj-1", "--status", "DONE"])

        assert result.exit_code == 0
        instance.update_status.assert_called_once()
        call_args = instance.update_status.call_args[0]
        assert call_args[0] == "proj-1"
        assert call_args[1].value == ToDoStatusEnum.DONE.value

    def test_update_name(self):
        with patch("sandpiper.plan.infrastructure.notion_project_repository.NotionProjectRepository") as MockRepo:
            instance = MockRepo.return_value

            result = self.runner.invoke(self.app, ["project", "update", "proj-1", "--name", "新しい名前"])

        assert result.exit_code == 0
        instance.update_name.assert_called_once_with("proj-1", "新しい名前")

    def test_update_without_options_exits_with_error(self):
        with patch("sandpiper.plan.infrastructure.notion_project_repository.NotionProjectRepository"):
            result = self.runner.invoke(self.app, ["project", "update", "proj-1"])

        assert result.exit_code == 1

    def test_update_invalid_status_exits_with_error(self):
        with patch("sandpiper.plan.infrastructure.notion_project_repository.NotionProjectRepository"):
            result = self.runner.invoke(self.app, ["project", "update", "proj-1", "--status", "INVALID"])

        assert result.exit_code == 1

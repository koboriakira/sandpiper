"""project-task サブコマンドのテスト"""

import json
import sys
from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from sandpiper.shared.repository.project_task_repository import InsertedProjectTask
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


def _make_task(task_id: str = "task-1", project_id: str = "proj-1") -> InsertedProjectTask:
    return InsertedProjectTask(
        id=task_id,
        title="テストタスク",
        status=ToDoStatusEnum.TODO,
        project_id=project_id,
    )


class TestProjectTaskGet:
    def setup_method(self):
        self.runner, self.app = _get_runner_and_app()

    def test_get_returns_json(self):
        with patch(
            "sandpiper.plan.infrastructure.notion_project_task_repository.NotionProjectTaskRepository"
        ) as MockRepo:
            instance = MockRepo.return_value
            instance.find.return_value = _make_task("task-abc")

            result = self.runner.invoke(self.app, ["project-task", "get", "task-abc"])

        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert data["id"] == "task-abc"
        assert data["title"] == "テストタスク"
        assert data["status"] == "ToDo"
        assert data["project_id"] == "proj-1"


class TestProjectTaskList:
    def setup_method(self):
        self.runner, self.app = _get_runner_and_app()

    def test_list_returns_json_array(self):
        tasks = [_make_task("t1"), _make_task("t2")]
        with patch(
            "sandpiper.plan.infrastructure.notion_project_task_repository.NotionProjectTaskRepository"
        ) as MockRepo:
            instance = MockRepo.return_value
            instance.fetch_all.return_value = tasks

            result = self.runner.invoke(self.app, ["project-task", "list"])

        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert len(data) == 2

    def test_list_filters_by_project_id(self):
        tasks = [
            _make_task("t1", project_id="proj-A"),
            _make_task("t2", project_id="proj-B"),
        ]
        with patch(
            "sandpiper.plan.infrastructure.notion_project_task_repository.NotionProjectTaskRepository"
        ) as MockRepo:
            instance = MockRepo.return_value
            instance.fetch_all.return_value = tasks

            result = self.runner.invoke(self.app, ["project-task", "list", "--project-id", "proj-A"])

        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert len(data) == 1
        assert data[0]["project_id"] == "proj-A"

    def test_list_filters_by_status(self):
        tasks = [
            _make_task("t1"),
            InsertedProjectTask(id="t2", title="完了タスク", status=ToDoStatusEnum.DONE, project_id="proj-1"),
        ]
        with patch(
            "sandpiper.plan.infrastructure.notion_project_task_repository.NotionProjectTaskRepository"
        ) as MockRepo:
            instance = MockRepo.return_value
            instance.fetch_all.return_value = tasks

            result = self.runner.invoke(self.app, ["project-task", "list", "--status", "TODO"])

        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert len(data) == 1
        assert data[0]["id"] == "t1"


class TestProjectTaskUpdate:
    def setup_method(self):
        self.runner, self.app = _get_runner_and_app()

    def test_update_status(self):
        with patch(
            "sandpiper.plan.infrastructure.notion_project_task_repository.NotionProjectTaskRepository"
        ) as MockRepo:
            instance = MockRepo.return_value

            result = self.runner.invoke(self.app, ["project-task", "update", "task-1", "--status", "IN_PROGRESS"])

        assert result.exit_code == 0
        instance.update_status.assert_called_once()
        call_args = instance.update_status.call_args[0]
        assert call_args[0] == "task-1"
        assert call_args[1].value == ToDoStatusEnum.IN_PROGRESS.value

    def test_update_title(self):
        with patch(
            "sandpiper.plan.infrastructure.notion_project_task_repository.NotionProjectTaskRepository"
        ) as MockRepo:
            instance = MockRepo.return_value

            result = self.runner.invoke(self.app, ["project-task", "update", "task-1", "--title", "新しいタイトル"])

        assert result.exit_code == 0
        instance.update_title.assert_called_once_with("task-1", "新しいタイトル")

    def test_update_without_options_exits_with_error(self):
        with patch("sandpiper.plan.infrastructure.notion_project_task_repository.NotionProjectTaskRepository"):
            result = self.runner.invoke(self.app, ["project-task", "update", "task-1"])

        assert result.exit_code == 1

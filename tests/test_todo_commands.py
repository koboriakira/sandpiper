"""todo サブコマンドのテスト"""

import json
import sys
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from sandpiper.perform.domain.todo import ToDo
from sandpiper.shared.valueobject.task_chute_section import TaskChuteSection
from sandpiper.shared.valueobject.todo_status_enum import ToDoStatusEnum

JST = timezone(timedelta(hours=9))


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


def _make_todo(todo_id: str = "todo-1") -> ToDo:
    return ToDo(
        id=todo_id,
        title="テストTODO",
        status=ToDoStatusEnum.TODO,
        section=TaskChuteSection.B_10_13,
        contexts=[],
    )


class TestTodoGet:
    def setup_method(self):
        self.runner, self.app = _get_runner_and_app()

    def test_get_returns_json(self):
        with patch("sandpiper.perform.infrastructure.notion_todo_repository.NotionTodoRepository") as MockRepo:
            instance = MockRepo.return_value
            instance.find.return_value = _make_todo("todo-abc")

            result = self.runner.invoke(self.app, ["todo", "get", "todo-abc"])

        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert data["id"] == "todo-abc"
        assert data["title"] == "テストTODO"
        assert data["status"] == "ToDo"
        assert data["section"] == "B_10_13"


class TestTodoList:
    def setup_method(self):
        self.runner, self.app = _get_runner_and_app()

    def test_list_defaults_to_todo_status(self):
        todos = [_make_todo("t1"), _make_todo("t2")]
        with patch("sandpiper.perform.infrastructure.notion_todo_repository.NotionTodoRepository") as MockRepo:
            instance = MockRepo.return_value
            instance.find_by_status.return_value = todos

            result = self.runner.invoke(self.app, ["todo", "list"])

        assert result.exit_code == 0
        instance.find_by_status.assert_called_once()
        call_args = instance.find_by_status.call_args[0]
        assert call_args[0].value == ToDoStatusEnum.TODO.value
        data = json.loads(result.stdout)
        assert len(data) == 2

    def test_list_all_calls_fetch_all(self):
        todos = [_make_todo("t1")]
        with patch("sandpiper.perform.infrastructure.notion_todo_repository.NotionTodoRepository") as MockRepo:
            instance = MockRepo.return_value
            instance.fetch_all.return_value = todos

            result = self.runner.invoke(self.app, ["todo", "list", "--status", "ALL"])

        assert result.exit_code == 0
        instance.fetch_all.assert_called_once()

    def test_list_invalid_status_exits_with_error(self):
        with patch("sandpiper.perform.infrastructure.notion_todo_repository.NotionTodoRepository"):
            result = self.runner.invoke(self.app, ["todo", "list", "--status", "INVALID"])

        assert result.exit_code == 1

    def _make_todo_with_schedule(self, todo_id: str, scheduled_start: datetime | None) -> ToDo:
        return ToDo(
            id=todo_id,
            title="スケジュール付きTODO",
            status=ToDoStatusEnum.TODO,
            contexts=[],
            scheduled_start_datetime=scheduled_start,
        )

    def test_scheduled_flag_filters_out_todos_without_schedule(self):
        no_schedule = _make_todo("t1")
        with_schedule = self._make_todo_with_schedule("t2", datetime(2026, 3, 10, 12, 0, tzinfo=JST))
        todos = [no_schedule, with_schedule]

        with patch("sandpiper.perform.infrastructure.notion_todo_repository.NotionTodoRepository") as MockRepo:
            instance = MockRepo.return_value
            instance.find_by_status.return_value = todos

            result = self.runner.invoke(self.app, ["todo", "list", "--scheduled"])

        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert len(data) == 1
        assert data[0]["id"] == "t2"

    def test_all_day_flag_filters_to_all_day_events(self):
        all_day = self._make_todo_with_schedule("t1", datetime(2026, 3, 10, 0, 0, tzinfo=JST))
        timed = self._make_todo_with_schedule("t2", datetime(2026, 3, 10, 12, 0, tzinfo=JST))
        no_schedule = _make_todo("t3")
        todos = [all_day, timed, no_schedule]

        with patch("sandpiper.perform.infrastructure.notion_todo_repository.NotionTodoRepository") as MockRepo:
            instance = MockRepo.return_value
            instance.find_by_status.return_value = todos

            result = self.runner.invoke(self.app, ["todo", "list", "--all-day"])

        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert len(data) == 1
        assert data[0]["id"] == "t1"

    def test_from_to_filters_by_time_range(self):
        before = self._make_todo_with_schedule("t1", datetime(2026, 3, 10, 11, 0, tzinfo=JST))
        in_range = self._make_todo_with_schedule("t2", datetime(2026, 3, 10, 12, 0, tzinfo=JST))
        after = self._make_todo_with_schedule("t3", datetime(2026, 3, 10, 16, 0, tzinfo=JST))
        todos = [before, in_range, after]

        with patch("sandpiper.perform.infrastructure.notion_todo_repository.NotionTodoRepository") as MockRepo:
            instance = MockRepo.return_value
            instance.find_by_status.return_value = todos

            result = self.runner.invoke(self.app, ["todo", "list", "--from", "12:00", "--to", "15:00"])

        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert len(data) == 1
        assert data[0]["id"] == "t2"


class TestTodoUpdate:
    def setup_method(self):
        self.runner, self.app = _get_runner_and_app()

    def test_update_status(self):
        with patch("sandpiper.perform.infrastructure.notion_todo_repository.NotionTodoRepository") as MockRepo:
            instance = MockRepo.return_value

            result = self.runner.invoke(self.app, ["todo", "update", "todo-1", "--status", "DONE"])

        assert result.exit_code == 0
        instance.update_status.assert_called_once()
        call_args = instance.update_status.call_args[0]
        assert call_args[0] == "todo-1"
        assert call_args[1].value == ToDoStatusEnum.DONE.value

    def test_update_section(self):
        with patch("sandpiper.perform.infrastructure.notion_todo_repository.NotionTodoRepository") as MockRepo:
            instance = MockRepo.return_value

            result = self.runner.invoke(self.app, ["todo", "update", "todo-1", "--section", "C_13_17"])

        assert result.exit_code == 0
        instance.update_section.assert_called_once()
        call_args = instance.update_section.call_args[0]
        assert call_args[0] == "todo-1"
        assert call_args[1].value == TaskChuteSection.C_13_17.value

    def test_update_title(self):
        with patch("sandpiper.perform.infrastructure.notion_todo_repository.NotionTodoRepository") as MockRepo:
            instance = MockRepo.return_value

            result = self.runner.invoke(self.app, ["todo", "update", "todo-1", "--title", "新しいタイトル"])

        assert result.exit_code == 0
        instance.update_title.assert_called_once_with("todo-1", "新しいタイトル")

    def test_update_without_options_exits_with_error(self):
        with patch("sandpiper.perform.infrastructure.notion_todo_repository.NotionTodoRepository"):
            result = self.runner.invoke(self.app, ["todo", "update", "todo-1"])

        assert result.exit_code == 1

    def test_update_invalid_section_exits_with_error(self):
        with patch("sandpiper.perform.infrastructure.notion_todo_repository.NotionTodoRepository"):
            result = self.runner.invoke(self.app, ["todo", "update", "todo-1", "--section", "X_INVALID"])

        assert result.exit_code == 1

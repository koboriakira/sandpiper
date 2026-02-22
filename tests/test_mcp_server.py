"""MCPサーバーのテスト"""

from datetime import datetime
from unittest.mock import MagicMock, patch
from zoneinfo import ZoneInfo

from sandpiper.perform.domain.todo import ToDo
from sandpiper.shared.valueobject.task_chute_section import TaskChuteSection
from sandpiper.shared.valueobject.todo_status_enum import ToDoStatusEnum

JST = ZoneInfo("Asia/Tokyo")


def _make_todo(
    id: str = "page-id-1",
    title: str = "テストタスク",
    status: ToDoStatusEnum = ToDoStatusEnum.IN_PROGRESS,
    section: TaskChuteSection | None = TaskChuteSection.B_10_13,
    log_start_datetime: datetime | None = None,
) -> ToDo:
    return ToDo(
        id=id,
        title=title,
        status=status,
        section=section,
        log_start_datetime=log_start_datetime or datetime(2026, 2, 23, 10, 0, tzinfo=JST),
    )


class TestGetInProgressTodos:
    """get_in_progress_todosツール関数のテスト"""

    @patch("sandpiper.mcp_server.NotionTodoRepository")
    def test_returns_in_progress_todos(self, mock_repo_cls: MagicMock) -> None:
        """IN_PROGRESSのToDoが正しく返されるケース"""
        from sandpiper.mcp_server import get_in_progress_todos

        todo = _make_todo()
        mock_repo_cls.return_value.find_by_status.return_value = [todo]

        result = get_in_progress_todos()

        mock_repo_cls.return_value.find_by_status.assert_called_once()
        args = mock_repo_cls.return_value.find_by_status.call_args[0]
        assert args[0].value == ToDoStatusEnum.IN_PROGRESS.value
        assert len(result) == 1
        assert result[0]["id"] == "page-id-1"
        assert result[0]["title"] == "テストタスク"
        assert result[0]["status"] == "InProgress"
        assert result[0]["section"] == "B_10_13"
        assert result[0]["log_start_datetime"] == "2026-02-23T10:00:00+09:00"

    @patch("sandpiper.mcp_server.NotionTodoRepository")
    def test_returns_empty_list(self, mock_repo_cls: MagicMock) -> None:
        """空リストのケース"""
        from sandpiper.mcp_server import get_in_progress_todos

        mock_repo_cls.return_value.find_by_status.return_value = []

        result = get_in_progress_todos()

        assert result == []

    @patch("sandpiper.mcp_server.NotionTodoRepository")
    def test_handles_none_fields(self, mock_repo_cls: MagicMock) -> None:
        """section、log_start_datetimeがNoneのケース"""
        from sandpiper.mcp_server import get_in_progress_todos

        todo = _make_todo(section=None, log_start_datetime=None)
        todo.log_start_datetime = None
        mock_repo_cls.return_value.find_by_status.return_value = [todo]

        result = get_in_progress_todos()

        assert result[0]["section"] is None
        assert result[0]["log_start_datetime"] is None

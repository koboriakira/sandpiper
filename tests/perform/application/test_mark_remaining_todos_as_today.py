"""MarkRemainingTodosAsToday ユースケースのテスト"""

from unittest.mock import MagicMock, call

import pytest

from sandpiper.perform.application.mark_remaining_todos_as_today import MarkRemainingTodosAsToday
from sandpiper.perform.domain.todo import ToDo
from sandpiper.perform.infrastructure.notion_todo_repository import NotionTodoRepository
from sandpiper.shared.valueobject.todo_status_enum import ToDoStatusEnum


class TestMarkRemainingTodosAsToday:
    @pytest.fixture()
    def repo(self) -> MagicMock:
        return MagicMock(spec=NotionTodoRepository)

    @pytest.fixture()
    def use_case(self, repo: MagicMock) -> MarkRemainingTodosAsToday:
        return MarkRemainingTodosAsToday(todo_repository=repo)

    def test_marks_in_progress_and_todo_tasks(self, use_case: MarkRemainingTodosAsToday, repo: MagicMock) -> None:
        """IN_PROGRESSとTODOの両方のタスクにフラグが付く"""
        in_progress_todo = ToDo(id="ip-1", title="進行中タスク", status=ToDoStatusEnum.IN_PROGRESS)
        todo_task = ToDo(id="todo-1", title="未着手タスク", status=ToDoStatusEnum.TODO)

        repo.find_by_status.side_effect = lambda status: {
            ToDoStatusEnum.IN_PROGRESS: [in_progress_todo],
            ToDoStatusEnum.TODO: [todo_task],
        }[status]

        result = use_case.execute()

        assert result.marked_count == 2
        repo.mark_as_today.assert_has_calls([call("ip-1"), call("todo-1")], any_order=False)

    def test_no_incomplete_tasks(self, use_case: MarkRemainingTodosAsToday, repo: MagicMock) -> None:
        """未完了タスクがない場合は0件"""
        repo.find_by_status.return_value = []

        result = use_case.execute()

        assert result.marked_count == 0
        repo.mark_as_today.assert_not_called()

    def test_multiple_tasks_per_status(self, use_case: MarkRemainingTodosAsToday, repo: MagicMock) -> None:
        """各ステータスに複数タスクがある場合すべてにフラグが付く"""
        ip_tasks = [ToDo(id=f"ip-{i}", title=f"進行中{i}", status=ToDoStatusEnum.IN_PROGRESS) for i in range(3)]
        todo_tasks = [ToDo(id=f"todo-{i}", title=f"未着手{i}", status=ToDoStatusEnum.TODO) for i in range(2)]

        repo.find_by_status.side_effect = lambda status: {
            ToDoStatusEnum.IN_PROGRESS: ip_tasks,
            ToDoStatusEnum.TODO: todo_tasks,
        }[status]

        result = use_case.execute()

        assert result.marked_count == 5
        assert repo.mark_as_today.call_count == 5

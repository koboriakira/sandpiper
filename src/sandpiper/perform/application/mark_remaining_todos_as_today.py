"""未完了タスクに「今日中にやる」フラグを付けるユースケース

TODOリストに残っているIN_PROGRESSおよびTODOステータスのタスクに
「今日中にやる」フラグを有効化する。
"""

from dataclasses import dataclass

from sandpiper.perform.infrastructure.notion_todo_repository import NotionTodoRepository
from sandpiper.shared.valueobject.todo_status_enum import ToDoStatusEnum


@dataclass
class MarkRemainingTodosAsTodayResult:
    """実行結果"""

    marked_count: int


class MarkRemainingTodosAsToday:
    """未完了タスクに「今日中にやる」フラグを一括設定するユースケース"""

    def __init__(self, todo_repository: NotionTodoRepository) -> None:
        self._todo_repository = todo_repository

    def execute(self) -> MarkRemainingTodosAsTodayResult:
        """IN_PROGRESSおよびTODOステータスのタスクに「今日中にやる」フラグを付ける

        Returns:
            MarkRemainingTodosAsTodayResult: フラグを付けたタスク数
        """
        marked_count = 0

        for status in [ToDoStatusEnum.IN_PROGRESS, ToDoStatusEnum.TODO]:
            todos = self._todo_repository.find_by_status(status)
            for todo in todos:
                self._todo_repository.mark_as_today(todo.id)
                marked_count += 1

        return MarkRemainingTodosAsTodayResult(marked_count=marked_count)

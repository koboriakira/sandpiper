from dataclasses import dataclass

from sandpiper.app.message_dispatcher import MessageDispatcher
from sandpiper.perform.domain.todo_repository import TodoRepository
from sandpiper.shared.event.todo_completed import TodoCompleted


@dataclass
class MarkDoneResult:
    completed_count: int
    completed_titles: list[str]


class MarkDone:
    """InProgress中のタスクをすべてDoneにするユースケース."""

    _todo_repository: TodoRepository
    _dispatcher: MessageDispatcher

    def __init__(self, todo_repository: TodoRepository, dispatcher: MessageDispatcher) -> None:
        self._todo_repository = todo_repository
        self._dispatcher = dispatcher

    def execute(self) -> MarkDoneResult:
        """InProgress中のタスクを検索し、すべてDoneにする."""
        in_progress_todos = self._todo_repository.find_in_progress()
        completed_titles: list[str] = []

        for todo in in_progress_todos:
            todo.complete()
            self._todo_repository.save(todo)
            self._dispatcher.publish(TodoCompleted(page_id=todo.id, title=todo.title))
            completed_titles.append(todo.title)

        return MarkDoneResult(
            completed_count=len(completed_titles),
            completed_titles=completed_titles,
        )

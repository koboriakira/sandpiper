from datetime import datetime

from sandpiper.app.message_dispatcher import MessageDispatcher
from sandpiper.perform.domain.todo_repository import TodoRepository
from sandpiper.shared.event.todo_completed import TodoCompleted
from sandpiper.shared.valueobject.todo_status_enum import ToDoStatusEnum


class CompleteTodo:
    _todo_repository: TodoRepository
    _dispatcher: MessageDispatcher

    def __init__(self, todo_repository: TodoRepository, dispatcher: MessageDispatcher) -> None:
        self._todo_repository = todo_repository
        self._dispatcher = dispatcher

    def execute(
        self,
        page_id: str,
        start_datetime: datetime | None = None,
        end_datetime: datetime | None = None,
    ) -> None:
        todo = self._todo_repository.find(page_id)
        if todo.status == ToDoStatusEnum.TODO and start_datetime is None:
            msg = "ステータスがTODOのタスクを完了するには開始時刻(--start)の指定が必要です"
            raise ValueError(msg)
        todo.complete(start_datetime=start_datetime, end_datetime=end_datetime)
        self._todo_repository.save(todo)
        self._dispatcher.publish(TodoCompleted(page_id=page_id, title=todo.title))

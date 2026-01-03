from sandpiper.app.message_dispatcher import MessageDispatcher
from sandpiper.perform.domain.todo_repository import TodoRepository
from sandpiper.shared.event.todo_completed import TodoCompleted


class CompleteTodo:
    _todo_repository: TodoRepository
    _dispatcher: MessageDispatcher

    def __init__(self, todo_repository: TodoRepository, dispatcher: MessageDispatcher) -> None:
        self._todo_repository = todo_repository
        self._dispatcher = dispatcher

    def execute(self, page_id: str) -> None:
        todo = self._todo_repository.find(page_id)
        todo.complete()
        self._todo_repository.save(todo)
        self._dispatcher.publish(TodoCompleted(page_id=page_id, title=todo.title))

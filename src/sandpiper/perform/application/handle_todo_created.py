from sandpiper.perform.domain.todo_repository import TodoRepository
from sandpiper.shared.event.todo_created import TodoCreated


class HandleTodoCreated:
    _todo_repository: TodoRepository

    def __init__(self, todo_repository: TodoRepository) -> None:
        self._todo_repository = todo_repository

    def __call__(self, event: TodoCreated) -> None:
        print(f"ToDo created with page ID: {event.page_id}")
        todo = self._todo_repository.find(event.page_id)
        todo.start()
        self._todo_repository.save(todo)

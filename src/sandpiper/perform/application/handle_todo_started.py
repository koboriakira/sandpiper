from sandpiper.perform.domain.todo_repository import TodoRepository
from sandpiper.shared.event.todo_created import TodoStarted


class HandleTodoStarted:
    _todo_repository: TodoRepository

    def __init__(self, todo_repository: TodoRepository):
        self._todo_repository = todo_repository

    def __call__(self, event: TodoStarted):
        print(f"ToDo started with page ID: {event.page_id}")
        todo = self._todo_repository.find(event.page_id)
        todo.start()
        self._todo_repository.save(todo)

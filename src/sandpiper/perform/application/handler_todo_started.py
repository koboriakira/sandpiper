from sandpiper.perform.domain.todo_repository import TodoRepository
from sandpiper.perform.infrastructure.notion_todo_repository import NotionTodoRepository
from sandpiper.shared.event.todo_created import TodoStarted


class HandleTodoStarted:
    _todo_repository: TodoRepository

    def __init__(self):
        self._todo_repository = NotionTodoRepository()

    def __call__(self, event: TodoStarted):
        print(f"ToDo started with page ID: {event.page_id}")
        todo = self._todo_repository.find(event.page_id)
        todo.inprogress()
        self._todo_repository.save(todo)

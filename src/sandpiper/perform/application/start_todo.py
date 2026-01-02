from sandpiper.perform.domain.todo_repository import TodoRepository


class StartTodo:
    _todo_repository: TodoRepository

    def __init__(self, todo_repository: TodoRepository):
        self._todo_repository = todo_repository

    def execute(self, page_id: str):
        todo = self._todo_repository.find(page_id)
        todo.start()
        self._todo_repository.save(todo)

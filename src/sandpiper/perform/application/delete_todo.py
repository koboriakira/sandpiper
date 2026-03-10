from sandpiper.perform.infrastructure.notion_todo_repository import NotionTodoRepository


class DeleteTodo:
    _todo_repository: NotionTodoRepository

    def __init__(self, todo_repository: NotionTodoRepository) -> None:
        self._todo_repository = todo_repository

    def execute(self, page_id: str) -> None:
        self._todo_repository.delete(page_id)

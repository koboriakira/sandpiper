from sandpiper.perform.domain.todo_repository import TodoRepository
from sandpiper.shared.event.todo_created import TodoStarted
from sandpiper.shared.valueobject.todo_status_enum import ToDoStatusEnum


class HandleTodoStarted:
    _todo_repository: TodoRepository

    def __init__(self, todo_repository: TodoRepository) -> None:
        self._todo_repository = todo_repository

    def __call__(self, event: TodoStarted) -> None:
        print(f"ToDo started with page ID: {event.page_id}")
        todo = self._todo_repository.find(event.page_id)

        # すでに開始されている場合は処理をスキップ(StartTodoからの呼び出し時)
        if todo.status == ToDoStatusEnum.IN_PROGRESS:
            return

        # CreateTodo(enableStart=True)からの呼び出し時はここで開始処理を行う
        todo.start()
        self._todo_repository.save(todo)

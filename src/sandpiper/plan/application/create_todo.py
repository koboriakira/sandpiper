from dataclasses import dataclass

from sandpiper.app.message_dispatcher import MessageDispatcher
from sandpiper.plan.domain.todo import ToDo, ToDoKind
from sandpiper.plan.domain.todo_repository import TodoRepository
from sandpiper.plan.infrastructure.notion_todo_repository import NotionTodoRepository
from sandpiper.shared.event.todo_created import TodoStarted
from sandpiper.shared.valueobject.task_chute_section import TaskChuteSection


@dataclass
class CreateNewToDoRequest:
    title: str
    kind: ToDoKind | None = None
    section: TaskChuteSection | None = None


@dataclass
class CreateToDo:
    _dispatcher: MessageDispatcher
    _todo_repository: TodoRepository

    def __init__(self, dispatcher: MessageDispatcher):
        self._dispatcher = dispatcher
        self._todo_repository = NotionTodoRepository()

    def execute(self, request: CreateNewToDoRequest, enableStart: bool = False):
        todo = ToDo(
            title=request.title,
            kind=request.kind,
            section=request.section,
        )
        inserted_todo = self._todo_repository.save(todo)
        print(f"Created ToDo: {inserted_todo}")
        if enableStart:
            self._dispatcher.publish(TodoStarted(page_id=inserted_todo.id))


if __name__ == "__main__":
    # uv run python -m src.sandpiper.plan.application.create_todo
    from sandpiper.app.app import bootstrap

    app = bootstrap()
    app.create_todo.execute(
        CreateNewToDoRequest(
            title="新しいToDoタスク",
        ),
        enableStart=True,
    )

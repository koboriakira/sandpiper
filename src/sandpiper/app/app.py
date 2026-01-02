from sandpiper.app.message_dispatcher import MessageDispatcher
from sandpiper.perform.application.handle_todo_started import HandleTodoStarted
from sandpiper.perform.infrastructure.notion_todo_repository import NotionTodoRepository as PerformNotionTodoRepository
from sandpiper.plan.application.create_todo import CreateToDo
from sandpiper.plan.infrastructure.notion_todo_repository import NotionTodoRepository as PlanNotionTodoRepository
from sandpiper.shared.event.todo_created import TodoStarted
from sandpiper.shared.infrastructure.event_bus import EventBus


class SandPiperApp:
    def __init__(self, create_todo: CreateToDo):
        self.create_todo = create_todo


def bootstrap() -> SandPiperApp:
    event_bus = EventBus()

    # Subscribe event handlers
    handle_todo_started = HandleTodoStarted(PerformNotionTodoRepository())
    event_bus.subscribe(TodoStarted, handle_todo_started)
    dispatcher = MessageDispatcher(event_bus)

    # Create application services
    create_todo = CreateToDo(
        dispatcher=dispatcher,
        todo_repository=PlanNotionTodoRepository(),
    )
    return SandPiperApp(
        create_todo=create_todo,
    )

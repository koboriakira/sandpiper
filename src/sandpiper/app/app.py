from sandpiper.app.message_dispatcher import MessageDispatcher
from sandpiper.perform.application.handler_todo_started import HandleTodoStarted
from sandpiper.plan.application.create_todo import CreateToDo
from sandpiper.shared.event.todo_created import TodoStarted
from sandpiper.shared.infrastructure.event_bus import EventBus


class SandPiperApp:
    def __init__(self, create_todo: CreateToDo):
        self.create_todo = create_todo


def bootstrap() -> SandPiperApp:
    event_bus = EventBus()
    event_bus.subscribe(TodoStarted, HandleTodoStarted())
    dispatcher = MessageDispatcher(event_bus)

    create_todo = CreateToDo(dispatcher=dispatcher)
    return SandPiperApp(
        create_todo=create_todo,
    )

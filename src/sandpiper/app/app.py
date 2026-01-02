from sandpiper.app.message_dispatcher import MessageDispatcher
from sandpiper.perform.application.handle_todo_started import HandleTodoStarted
from sandpiper.perform.infrastructure.notion_todo_repository import NotionTodoRepository as PerformNotionTodoRepository
from sandpiper.plan.application.create_repeat_project_task import CreateRepeatProjectTask
from sandpiper.plan.application.create_repeat_task import CreateRepeatTask
from sandpiper.plan.application.create_todo import CreateToDo
from sandpiper.plan.infrastructure.notion_todo_repository import NotionTodoRepository as PlanNotionTodoRepository
from sandpiper.plan.query.project_task_query import NotionProjectTaskQuery
from sandpiper.plan.query.routine_query import NotionRoutineQuery
from sandpiper.review.application.get_todo_log import GetTodoLog
from sandpiper.review.query.todo_query import NotionTodoQuery
from sandpiper.shared.event.todo_created import TodoStarted
from sandpiper.shared.infrastructure.event_bus import EventBus


class SandPiperApp:
    def __init__(
        self,
        create_todo: CreateToDo,
        create_repeat_task: CreateRepeatTask,
        create_repeat_project_task: CreateRepeatProjectTask,
        get_todo_log: GetTodoLog,
    ) -> None:
        self.create_todo = create_todo
        self.create_repeat_task = create_repeat_task
        self.create_repeat_project_task = create_repeat_project_task
        self.get_todo_log = get_todo_log


def bootstrap() -> SandPiperApp:
    event_bus = EventBus()

    # infrastructure setup
    routine_query = NotionRoutineQuery()
    project_task_query = NotionProjectTaskQuery()
    todo_query = NotionTodoQuery()
    plan_notion_todo_repository = PlanNotionTodoRepository()
    perform_notion_todo_repository = PerformNotionTodoRepository()

    # Subscribe event handlers
    handle_todo_started = HandleTodoStarted(perform_notion_todo_repository)
    event_bus.subscribe(TodoStarted, handle_todo_started)
    dispatcher = MessageDispatcher(event_bus)

    # Create application services
    return SandPiperApp(
        create_todo=CreateToDo(
            dispatcher=dispatcher,
            todo_repository=plan_notion_todo_repository,
        ),
        create_repeat_task=CreateRepeatTask(
            routine_query=routine_query,
            todo_repository=plan_notion_todo_repository,
        ),
        create_repeat_project_task=CreateRepeatProjectTask(
            project_task_query=project_task_query,
            todo_repository=plan_notion_todo_repository,
        ),
        get_todo_log=GetTodoLog(
            todo_query=todo_query,
        ),
    )

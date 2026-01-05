from sandpiper.app.message_dispatcher import MessageDispatcher
from sandpiper.calendar.application.create_calendar_event import CreateCalendarEvent
from sandpiper.calendar.application.delete_calendar_events import DeleteCalendarEvents
from sandpiper.calendar.infrastructure.notion_calendar_repository import NotionCalendarRepository
from sandpiper.perform.application.complete_todo import CompleteTodo
from sandpiper.perform.application.handle_todo_started import HandleTodoStarted
from sandpiper.perform.application.start_todo import StartTodo
from sandpiper.perform.infrastructure.notion_todo_repository import NotionTodoRepository as PerformNotionTodoRepository
from sandpiper.plan.application.create_project import CreateProject
from sandpiper.plan.application.create_repeat_project_task import CreateRepeatProjectTask
from sandpiper.plan.application.create_repeat_task import CreateRepeatTask
from sandpiper.plan.application.create_todo import CreateToDo
from sandpiper.plan.application.handle_completed_task import HandleCompletedTask
from sandpiper.plan.infrastructure.notion_project_repository import NotionProjectRepository
from sandpiper.plan.infrastructure.notion_routine_repository import NotionRoutineRepository
from sandpiper.plan.infrastructure.notion_todo_repository import NotionTodoRepository as PlanNotionTodoRepository
from sandpiper.plan.query.project_task_query import NotionProjectTaskQuery
from sandpiper.review.application.get_github_activity import GetGitHubActivity
from sandpiper.review.application.get_todo_log import GetTodoLog
from sandpiper.review.query.github_activity_query import GitHubActivityQuery
from sandpiper.review.query.todo_query import NotionTodoQuery
from sandpiper.shared.event.todo_completed import TodoCompleted
from sandpiper.shared.event.todo_created import TodoStarted
from sandpiper.shared.infrastructure.event_bus import EventBus
from sandpiper.shared.infrastructure.github_client import GitHubClient
from sandpiper.shared.infrastructure.notion_commentator import NotionCommentator
from sandpiper.shared.infrastructure.slack_notice_messanger import SlackNoticeMessanger


class SandPiperApp:
    def __init__(
        self,
        create_todo: CreateToDo,
        create_project: CreateProject,
        create_repeat_task: CreateRepeatTask,
        create_repeat_project_task: CreateRepeatProjectTask,
        get_todo_log: GetTodoLog,
        get_github_activity: GetGitHubActivity,
        start_todo: StartTodo,
        complete_todo: CompleteTodo,
        create_calendar_event: CreateCalendarEvent,
        delete_calendar_events: DeleteCalendarEvents,
    ) -> None:
        self.create_todo = create_todo
        self.create_project = create_project
        self.create_repeat_task = create_repeat_task
        self.create_repeat_project_task = create_repeat_project_task
        self.get_todo_log = get_todo_log
        self.get_github_activity = get_github_activity
        self.start_todo = start_todo
        self.complete_todo = complete_todo
        self.create_calendar_event = create_calendar_event
        self.delete_calendar_events = delete_calendar_events


def bootstrap() -> SandPiperApp:
    event_bus = EventBus()

    # infrastructure setup
    project_task_query = NotionProjectTaskQuery()
    todo_query = NotionTodoQuery()
    plan_notion_todo_repository = PlanNotionTodoRepository()
    perform_notion_todo_repository = PerformNotionTodoRepository()
    routine_repository = NotionRoutineRepository()
    project_repository = NotionProjectRepository()
    calendar_repository = NotionCalendarRepository()
    default_notice_messanger = SlackNoticeMessanger(channel_id="C04Q3AV4TA5")
    commentator = NotionCommentator()

    # GitHub integration setup
    github_client = GitHubClient()
    github_activity_query = GitHubActivityQuery(github_client)

    # Subscribe event handlers
    handle_todo_started = HandleTodoStarted(perform_notion_todo_repository)
    event_bus.subscribe(TodoStarted, handle_todo_started)
    handle_todo_completed = HandleCompletedTask(plan_notion_todo_repository, default_notice_messanger, commentator)
    event_bus.subscribe(TodoCompleted, handle_todo_completed)

    # Create message dispatcher
    dispatcher = MessageDispatcher(event_bus)

    # Create application services
    return SandPiperApp(
        create_todo=CreateToDo(
            dispatcher=dispatcher,
            todo_repository=plan_notion_todo_repository,
        ),
        create_project=CreateProject(
            project_repository=project_repository,
        ),
        create_repeat_task=CreateRepeatTask(
            routine_repository=routine_repository,
            todo_repository=plan_notion_todo_repository,
        ),
        create_repeat_project_task=CreateRepeatProjectTask(
            project_task_query=project_task_query,
            todo_repository=plan_notion_todo_repository,
        ),
        get_todo_log=GetTodoLog(
            todo_query=todo_query,
        ),
        get_github_activity=GetGitHubActivity(
            github_activity_query=github_activity_query,
        ),
        start_todo=StartTodo(
            todo_repository=perform_notion_todo_repository,
        ),
        complete_todo=CompleteTodo(
            todo_repository=perform_notion_todo_repository,
            dispatcher=dispatcher,
        ),
        create_calendar_event=CreateCalendarEvent(
            calendar_repository=calendar_repository,
        ),
        delete_calendar_events=DeleteCalendarEvents(
            calendar_repository=calendar_repository,
        ),
    )

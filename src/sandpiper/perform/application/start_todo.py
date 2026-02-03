from sandpiper.app.message_dispatcher import MessageDispatcher
from sandpiper.perform.domain.todo_repository import TodoRepository
from sandpiper.shared.event.todo_started import TodoStarted
from sandpiper.shared.repository.project_task_repository import ProjectTaskRepository
from sandpiper.shared.utils.date_utils import jst_now
from sandpiper.shared.valueobject.todo_status_enum import ToDoStatusEnum


class StartTodo:
    _todo_repository: TodoRepository
    _project_task_repository: ProjectTaskRepository
    _dispatcher: MessageDispatcher

    def __init__(
        self,
        todo_repository: TodoRepository,
        project_task_repository: ProjectTaskRepository,
        dispatcher: MessageDispatcher,
    ) -> None:
        self._todo_repository = todo_repository
        self._project_task_repository = project_task_repository
        self._dispatcher = dispatcher

    def execute(self, page_id: str) -> None:
        todo = self._todo_repository.find(page_id)
        todo.start()
        self._todo_repository.save(todo)

        if todo.project_task_page_id:
            self._start_project_task_if_not_in_progress(todo.project_task_page_id)

        context = todo.contexts[0] if todo.contexts else None
        self._dispatcher.publish(
            TodoStarted(
                name=todo.title,
                execution_time=jst_now(),
                context=context,
                scheduled_duration=todo.scheduled_duration,
            )
        )

    def _start_project_task_if_not_in_progress(self, project_task_page_id: str) -> None:
        """プロジェクトタスクがInProgressでなければInProgressに更新する"""
        project_task = self._project_task_repository.find(project_task_page_id)
        if project_task.status != ToDoStatusEnum.IN_PROGRESS:
            self._project_task_repository.update_status(project_task_page_id, ToDoStatusEnum.IN_PROGRESS)

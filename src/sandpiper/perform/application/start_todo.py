from sandpiper.perform.domain.todo_repository import TodoRepository
from sandpiper.plan.domain.project_task_repository import ProjectTaskRepository


class StartTodo:
    _todo_repository: TodoRepository
    _project_task_repository: ProjectTaskRepository

    def __init__(
        self,
        todo_repository: TodoRepository,
        project_task_repository: ProjectTaskRepository,
    ) -> None:
        self._todo_repository = todo_repository
        self._project_task_repository = project_task_repository

    def execute(self, page_id: str) -> None:
        todo = self._todo_repository.find(page_id)
        todo.start()
        self._todo_repository.save(todo)

        if todo.project_task_page_id:
            self._project_task_repository.start(todo.project_task_page_id)

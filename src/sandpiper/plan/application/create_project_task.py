from dataclasses import dataclass

from sandpiper.plan.domain.project_task import ProjectTask
from sandpiper.plan.domain.project_task_repository import ProjectTaskRepository
from sandpiper.shared.valueobject.todo_status_enum import ToDoStatusEnum


@dataclass
class CreateProjectTaskRequest:
    """プロジェクトタスク作成リクエスト"""

    title: str
    project_id: str
    status: ToDoStatusEnum = ToDoStatusEnum.TODO


@dataclass
class CreateProjectTask:
    """プロジェクトタスク作成ユースケース"""

    _project_task_repository: ProjectTaskRepository

    def __init__(self, project_task_repository: ProjectTaskRepository) -> None:
        self._project_task_repository = project_task_repository

    def execute(self, request: CreateProjectTaskRequest) -> None:
        """プロジェクトタスクを作成する

        Args:
            request: プロジェクトタスク作成リクエスト
        """
        project_task = ProjectTask(
            title=request.title,
            status=request.status,
            project_id=request.project_id,
        )
        inserted_project_task = self._project_task_repository.save(project_task)
        print(f"Created ProjectTask: {inserted_project_task}")

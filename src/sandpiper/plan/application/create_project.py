from dataclasses import dataclass
from datetime import date

from sandpiper.plan.domain.project import Project
from sandpiper.plan.domain.project_repository import ProjectRepository
from sandpiper.plan.domain.project_task import ProjectTask
from sandpiper.plan.domain.project_task_repository import ProjectTaskRepository
from sandpiper.shared.valueobject.todo_status_enum import ToDoStatusEnum


@dataclass
class CreateProjectRequest:
    """プロジェクト作成リクエスト"""

    name: str
    start_date: date
    end_date: date | None = None


@dataclass
class CreateProject:
    """プロジェクト作成ユースケース"""

    _project_repository: ProjectRepository
    _project_task_repository: ProjectTaskRepository

    def __init__(
        self,
        project_repository: ProjectRepository,
        project_task_repository: ProjectTaskRepository,
    ) -> None:
        self._project_repository = project_repository
        self._project_task_repository = project_task_repository

    def execute(self, request: CreateProjectRequest) -> None:
        project = Project(
            name=request.name,
            start_date=request.start_date,
            end_date=request.end_date,
        )
        inserted_project = self._project_repository.save(project)
        print(f"Created Project: {inserted_project}")

        # 同名のプロジェクトタスクを作成
        project_task = ProjectTask(
            title=request.name,
            status=ToDoStatusEnum.TODO,
            project_id=inserted_project.id,
        )
        inserted_project_task = self._project_task_repository.save(project_task)
        print(f"Created ProjectTask: {inserted_project_task}")

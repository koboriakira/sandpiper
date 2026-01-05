from dataclasses import dataclass
from datetime import date

from sandpiper.plan.domain.project import Project
from sandpiper.plan.domain.project_repository import ProjectRepository


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

    def __init__(self, project_repository: ProjectRepository) -> None:
        self._project_repository = project_repository

    def execute(self, request: CreateProjectRequest) -> None:
        project = Project(
            name=request.name,
            start_date=request.start_date,
            end_date=request.end_date,
        )
        inserted_project = self._project_repository.save(project)
        print(f"Created Project: {inserted_project}")

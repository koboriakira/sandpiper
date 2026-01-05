from dataclasses import dataclass

from sandpiper.plan.domain.project import Project
from sandpiper.plan.domain.project_repository import ProjectRepository
from sandpiper.plan.domain.project_task import ProjectTask
from sandpiper.plan.domain.project_task_repository import ProjectTaskRepository
from sandpiper.plan.domain.todo_repository import TodoRepository
from sandpiper.shared.utils.date_utils import jst_today
from sandpiper.shared.valueobject.todo_status_enum import ToDoStatusEnum


@dataclass
class ConvertToProjectResult:
    """TODOからプロジェクトへの変換結果"""

    project_id: str
    project_task_id: str
    title: str


@dataclass
class ConvertToProject:
    """TODOをプロジェクトに変換するユースケース"""

    _todo_repository: TodoRepository
    _project_repository: ProjectRepository
    _project_task_repository: ProjectTaskRepository

    def __init__(
        self,
        todo_repository: TodoRepository,
        project_repository: ProjectRepository,
        project_task_repository: ProjectTaskRepository,
    ) -> None:
        self._todo_repository = todo_repository
        self._project_repository = project_repository
        self._project_task_repository = project_task_repository

    def execute(self, page_id: str) -> ConvertToProjectResult:
        """TODOをプロジェクトに変換する

        Args:
            page_id: TODOデータベースのページID

        Returns:
            ConvertToProjectResult: 変換結果 (プロジェクトID、プロジェクトタスクID、タイトル)
        """
        # TODOページを取得
        todo = self._todo_repository.find(page_id)

        # 同名のプロジェクトを作成 (開始日は今日)
        project = Project(
            name=todo.title,
            start_date=jst_today(),
        )
        inserted_project = self._project_repository.save(project)

        # 同名のプロジェクトタスクを作成 (プロジェクトのRelationを設定)
        project_task = ProjectTask(
            title=todo.title,
            status=ToDoStatusEnum.TODO,
            project_id=inserted_project.id,
        )
        inserted_project_task = self._project_task_repository.save(project_task)

        return ConvertToProjectResult(
            project_id=inserted_project.id,
            project_task_id=inserted_project_task.id,
            title=todo.title,
        )

"""プロジェクトタスク自動整理ユースケース

親プロジェクトが完了済みまたは存在しないプロジェクトタスクを整理する。
"""

from dataclasses import dataclass, field

from sandpiper.plan.domain.project_repository import ProjectRepository
from sandpiper.shared.repository.project_task_repository import ProjectTaskRepository
from sandpiper.shared.valueobject.todo_status_enum import ToDoStatusEnum


@dataclass
class CleanupProjectTasksResult:
    completed_count: int = 0
    deleted_count: int = 0
    completed_titles: list[str] = field(default_factory=list)
    deleted_titles: list[str] = field(default_factory=list)

    @property
    def summary(self) -> str:
        return f"{self.completed_count}件完了, {self.deleted_count}件削除"


class CleanupProjectTasks:
    def __init__(
        self,
        project_task_repository: ProjectTaskRepository,
        project_repository: ProjectRepository,
    ) -> None:
        self.project_task_repository = project_task_repository
        self.project_repository = project_repository

    def execute(self) -> CleanupProjectTasksResult:
        tasks = self.project_task_repository.fetch_not_done()
        projects = self.project_repository.fetch_all()
        project_status_map = {p.id: p.status for p in projects}

        result = CleanupProjectTasksResult()

        for task in tasks:
            if not task.project_id or task.project_id not in project_status_map:
                # 親プロジェクトが存在しない → 削除
                self.project_task_repository.delete(task.id)
                result.deleted_count += 1
                result.deleted_titles.append(task.title)
            elif project_status_map[task.project_id] == ToDoStatusEnum.DONE:
                # 親プロジェクトがDone → タスクもDoneに
                self.project_task_repository.update_status(task.id, ToDoStatusEnum.DONE)
                result.completed_count += 1
                result.completed_titles.append(task.title)

        return result

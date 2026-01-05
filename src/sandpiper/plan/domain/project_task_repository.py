from typing import Protocol

from sandpiper.plan.domain.project_task import InsertedProjectTask, ProjectTask


class ProjectTaskRepository(Protocol):
    """プロジェクトタスクリポジトリのインターフェース"""

    def save(self, project_task: ProjectTask) -> InsertedProjectTask: ...

from typing import Protocol

from sandpiper.plan.domain.project_task import InsertedProjectTask, ProjectTask
from sandpiper.shared.valueobject.todo_status_enum import ToDoStatusEnum


class ProjectTaskRepository(Protocol):
    """プロジェクトタスクリポジトリのインターフェース"""

    def save(self, project_task: ProjectTask) -> InsertedProjectTask: ...

    def find(self, page_id: str) -> InsertedProjectTask: ...

    def update_status(self, page_id: str, status: ToDoStatusEnum) -> None: ...

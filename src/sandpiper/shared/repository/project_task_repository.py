from dataclasses import dataclass
from datetime import time
from typing import Protocol

from sandpiper.shared.valueobject.todo_status_enum import ToDoStatusEnum


@dataclass
class ProjectTask:
    """プロジェクトタスクエンティティ"""

    title: str
    status: ToDoStatusEnum
    project_id: str
    sort_order: str | None = None
    scheduled_start_time: time | None = None
    scheduled_end_time: time | None = None


@dataclass
class InsertedProjectTask:
    """作成されたプロジェクトタスク"""

    id: str
    title: str
    status: ToDoStatusEnum
    project_id: str
    sort_order: str | None = None
    scheduled_start_time: time | None = None
    scheduled_end_time: time | None = None


class ProjectTaskRepository(Protocol):
    """プロジェクトタスクリポジトリのインターフェース"""

    def save(self, project_task: ProjectTask) -> InsertedProjectTask: ...

    def find(self, page_id: str) -> InsertedProjectTask: ...

    def update_status(self, page_id: str, status: ToDoStatusEnum) -> None: ...

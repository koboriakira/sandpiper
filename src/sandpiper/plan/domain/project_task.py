from dataclasses import dataclass

from sandpiper.shared.valueobject.todo_status_enum import ToDoStatusEnum


@dataclass
class ProjectTask:
    """プロジェクトタスクエンティティ"""

    title: str
    status: ToDoStatusEnum
    project_id: str
    sort_order: str | None = None


@dataclass
class InsertedProjectTask:
    """作成されたプロジェクトタスク"""

    id: str
    title: str
    status: ToDoStatusEnum
    project_id: str
    sort_order: str | None = None

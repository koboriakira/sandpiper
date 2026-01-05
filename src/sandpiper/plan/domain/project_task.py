from dataclasses import dataclass

from sandpiper.shared.valueobject.todo_status_enum import ToDoStatusEnum


@dataclass
class ProjectTask:
    """プロジェクトタスクエンティティ"""

    title: str
    status: ToDoStatusEnum
    project_id: str


@dataclass
class InsertedProjectTask:
    """作成されたプロジェクトタスク"""

    id: str
    title: str
    status: ToDoStatusEnum
    project_id: str

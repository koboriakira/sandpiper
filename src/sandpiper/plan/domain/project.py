from dataclasses import dataclass
from datetime import date

from sandpiper.shared.valueobject.todo_status_enum import ToDoStatusEnum


@dataclass
class Project:
    """プロジェクトエンティティ"""

    name: str
    start_date: date
    end_date: date | None = None
    jira_url: str | None = None
    status: ToDoStatusEnum | None = None
    is_work: bool = False


@dataclass
class InsertedProject:
    """保存されたプロジェクトエンティティ"""

    id: str
    name: str
    start_date: date
    end_date: date | None = None
    jira_url: str | None = None
    status: ToDoStatusEnum | None = None
    is_work: bool = False

from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from sandpiper.shared.valueobject.task_chute_section import TaskChuteSection


class ToDoKind(Enum):
    SCHEDULE = "スケジュール"
    PROJECT = "プロジェクト"
    REPEAT = "リピート"
    INTERRUPTION = "差し込み"
    SINGLE = "単発"
    SUBTASK = "サブタスク"


class ToDoStatus(Enum):
    TODO = "ToDo"
    IN_PROGRESS = "InProgress"
    DONE = "Done"


@dataclass
class ToDo:
    title: str
    section: TaskChuteSection | None = None
    kind: ToDoKind | None = None
    project_page_id: str | None = None
    project_task_page_id: str | None = None
    routine_page_id: str | None = None
    execution_time: int | None = None
    context: list[str] | None = None
    sort_order: str | None = None
    scheduled_start_datetime: datetime | None = None
    scheduled_end_datetime: datetime | None = None


@dataclass
class InsertedToDo:
    id: str
    title: str
    section: TaskChuteSection | None = None
    kind: ToDoKind | None = None
    execution_time: int | None = None
    context: list[str] | None = None
    sort_order: str | None = None
    scheduled_start_datetime: datetime | None = None
    scheduled_end_datetime: datetime | None = None

from dataclasses import dataclass
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
    status: ToDoStatus
    section: TaskChuteSection | None = None
    kind: ToDoKind | None = None

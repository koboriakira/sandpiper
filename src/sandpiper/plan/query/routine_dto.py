from dataclasses import dataclass
from datetime import date

from sandpiper.shared.valueobject.task_chute_section import TaskChuteSection


@dataclass
class RoutineDto:
    title: str
    date: date
    section: TaskChuteSection


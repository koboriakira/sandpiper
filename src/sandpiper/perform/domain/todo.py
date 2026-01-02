from dataclasses import dataclass
from datetime import datetime

from sandpiper.shared.utils.date_utils import jst_now
from sandpiper.shared.valueobject.task_chute_section import TaskChuteSection
from sandpiper.shared.valueobject.todo_status_enum import ToDoStatusEnum


@dataclass
class ToDo:
    id: str
    title: str
    status: ToDoStatusEnum
    section: TaskChuteSection | None = None
    log_start_datetime: datetime | None = None
    log_end_datetime: datetime | None = None

    def inprogress(self) -> None:
        self.status = ToDoStatusEnum.IN_PROGRESS
        if self.section is None:
            self.section = TaskChuteSection.new()
        self.log_start_datetime = jst_now()
        self.log_end_datetime = None

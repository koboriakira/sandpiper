from dataclasses import dataclass, field
from datetime import datetime

from sandpiper.shared.utils.date_utils import jst_now
from sandpiper.shared.valueobject.context import Context
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
    project_task_page_id: str | None = None
    contexts: list[Context] = field(default_factory=list)

    def start(self) -> None:
        self.status = ToDoStatusEnum.IN_PROGRESS
        self.section = TaskChuteSection.new()
        self.log_start_datetime = jst_now()
        self.log_end_datetime = None

    def complete(self) -> None:
        self.status = ToDoStatusEnum.DONE
        self.log_end_datetime = jst_now()

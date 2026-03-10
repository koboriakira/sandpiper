from dataclasses import dataclass, field
from datetime import datetime, timedelta

from sandpiper.shared.utils.date_utils import jst_now
from sandpiper.shared.valueobject.context import Context
from sandpiper.shared.valueobject.task_chute_section import TaskChuteSection
from sandpiper.shared.valueobject.todo_kind import ToDoKind
from sandpiper.shared.valueobject.todo_status_enum import ToDoStatusEnum


@dataclass
class ToDo:
    id: str
    title: str
    status: ToDoStatusEnum
    kind: ToDoKind | None = None
    section: TaskChuteSection | None = None
    log_start_datetime: datetime | None = None
    log_end_datetime: datetime | None = None
    project_task_page_id: str | None = None
    contexts: list[Context] = field(default_factory=list)
    scheduled_start_datetime: datetime | None = None
    scheduled_end_datetime: datetime | None = None
    claude_url: str | None = None

    def start(self) -> None:
        self.status = ToDoStatusEnum.IN_PROGRESS
        self.section = TaskChuteSection.new()
        self.log_start_datetime = jst_now()
        self.log_end_datetime = None

    def complete(
        self,
        start_datetime: datetime | None = None,
        end_datetime: datetime | None = None,
    ) -> None:
        if start_datetime is not None:
            self.log_start_datetime = start_datetime
        self.status = ToDoStatusEnum.DONE
        self.log_end_datetime = end_datetime if end_datetime is not None else jst_now()

    @property
    def scheduled_duration(self) -> timedelta | None:
        """予定の開始時刻と終了時刻から所要時間を計算する"""
        if self.scheduled_start_datetime and self.scheduled_end_datetime:
            return self.scheduled_end_datetime - self.scheduled_start_datetime
        return None

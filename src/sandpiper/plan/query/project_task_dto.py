from dataclasses import dataclass, field
from datetime import date, datetime, time
from typing import Any

from sandpiper.plan.domain.todo import ToDo, ToDoKind
from sandpiper.shared.utils.date_utils import JST
from sandpiper.shared.valueobject.todo_status_enum import ToDoStatusEnum


@dataclass
class ProjectTaskDto:
    page_id: str
    title: str
    status: ToDoStatusEnum
    project_page_id: str
    is_next: bool
    block_children: list[Any] = field(default_factory=list)
    context: list[str] = field(default_factory=list)
    sort_order: str | None = None
    scheduled_start_time: time | None = None
    scheduled_end_time: time | None = None
    is_work_project: bool = False

    def to_todo_model(self, basis_date: date) -> ToDo:
        scheduled_start_datetime = None
        scheduled_end_datetime = None
        if self.scheduled_start_time:
            scheduled_start_datetime = datetime.combine(basis_date, self.scheduled_start_time, tzinfo=JST)
        if self.scheduled_end_time:
            scheduled_end_datetime = datetime.combine(basis_date, self.scheduled_end_time, tzinfo=JST)

        return ToDo(
            title=self.title,
            section=None,
            kind=ToDoKind.PROJECT,
            project_page_id=self.project_page_id,
            project_task_page_id=self.page_id,
            execution_time=30,
            context=self.context if self.context else None,
            sort_order=self.sort_order,
            scheduled_start_datetime=scheduled_start_datetime,
            scheduled_end_datetime=scheduled_end_datetime,
        )

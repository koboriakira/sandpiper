from dataclasses import dataclass, field
from typing import Any

from sandpiper.plan.domain.todo import ToDo, ToDoKind
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

    def to_todo_model(self) -> ToDo:
        return ToDo(
            title=self.title,
            section=None,
            kind=ToDoKind.PROJECT,
            project_page_id=self.project_page_id,
            project_task_page_id=self.page_id,
            execution_time=30,
            context=self.context if self.context else None,
        )

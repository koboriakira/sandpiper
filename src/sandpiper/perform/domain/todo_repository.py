from typing import Protocol

from sandpiper.perform.domain.todo import ToDo
from sandpiper.shared.valueobject.task_chute_section import TaskChuteSection
from sandpiper.shared.valueobject.todo_status_enum import ToDoStatusEnum


class TodoRepository(Protocol):
    def find(self, page_id: str) -> ToDo: ...

    def find_by_status(self, status: ToDoStatusEnum) -> list[ToDo]: ...

    def save(self, todo: ToDo) -> None: ...

    def update_section(self, page_id: str, section: TaskChuteSection) -> None: ...

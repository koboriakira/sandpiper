from typing import Protocol

from sandpiper.perform.domain.todo import ToDo
from sandpiper.shared.valueobject.task_chute_section import TaskChuteSection


class TodoRepository(Protocol):
    def find(self, page_id: str) -> ToDo: ...

    def save(self, todo: ToDo) -> None: ...

    def update_section(self, page_id: str, section: TaskChuteSection) -> None: ...

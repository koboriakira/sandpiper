from typing import Protocol

from sandpiper.perform.domain.todo import ToDo


class TodoRepository(Protocol):
    def find(self, page_id: str) -> ToDo: ...

    def save(self, todo: ToDo) -> None: ...

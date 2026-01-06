from typing import Protocol

from sandpiper.perform.domain.todo import ToDo


class TodoRepository(Protocol):
    def find(self, page_id: str) -> ToDo: ...

    def find_in_progress(self) -> list[ToDo]: ...

    def save(self, todo: ToDo) -> None: ...

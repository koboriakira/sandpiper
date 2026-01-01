from typing import Protocol

from sandpiper.plan.domain.todo import ToDo


class TodoRepository(Protocol):
    def save(self, todo: ToDo) -> None: ...

    def fetch(self) -> list[ToDo]: ...

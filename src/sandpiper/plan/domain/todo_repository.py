from typing import Any, Protocol

from sandpiper.plan.domain.todo import InsertedToDo, ToDo


class TodoRepository(Protocol):
    def save(self, todo: ToDo, options: dict[str, Any] | None = None) -> InsertedToDo: ...

    def fetch(self) -> list[ToDo]: ...

    def find(self, page_id: str) -> ToDo: ...

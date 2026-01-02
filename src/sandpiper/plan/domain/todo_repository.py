from typing import Protocol

from sandpiper.plan.domain.todo import InsertedToDo, ToDo


class TodoRepository(Protocol):
    def save(self, todo: ToDo) -> InsertedToDo: ...

    def fetch(self) -> list[ToDo]: ...

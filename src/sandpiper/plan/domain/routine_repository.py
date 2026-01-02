from typing import Protocol

from sandpiper.plan.domain.routine import Routine


class RoutineRepository(Protocol):
    def fetch(self) -> list[Routine]: ...

    def update(self, routine: Routine) -> None: ...

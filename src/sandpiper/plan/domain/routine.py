from dataclasses import dataclass, field
from datetime import date as Date
from typing import Any

from sandpiper.plan.domain.routine_cycle import RoutineCycle
from sandpiper.shared.valueobject.task_chute_section import TaskChuteSection


@dataclass
class Routine:
    id: str
    title: str
    date: Date
    section: TaskChuteSection
    cycle: RoutineCycle
    execution_time: int | None = None
    block_children: list[Any] = field(default_factory=list)
    context: list[str] = field(default_factory=list)
    sort_order: str | None = None

    def next_cycle(self, basis_date: Date | None = None) -> "Routine":
        next_date = self.cycle.next_date(basis_date=basis_date or self.date)
        return Routine(
            id=self.id,
            title=self.title,
            date=next_date,
            section=self.section,
            cycle=self.cycle,
            execution_time=self.execution_time,
            block_children=self.block_children,
            context=self.context,
            sort_order=self.sort_order,
        )

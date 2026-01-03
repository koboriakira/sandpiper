from dataclasses import dataclass
from datetime import date as Date

from sandpiper.plan.domain.routine_cycle import RoutineCycle
from sandpiper.shared.valueobject.task_chute_section import TaskChuteSection


@dataclass
class Routine:
    id: str
    title: str
    date: Date
    section: TaskChuteSection
    cycle: RoutineCycle

    def next_cycle(self, basis_date: Date | None = None) -> "Routine":
        next_date = self.cycle.next_date(basis_date=basis_date or self.date)
        return Routine(
            id=self.id,
            title=self.title,
            date=next_date,
            section=self.section,
            cycle=self.cycle,
        )

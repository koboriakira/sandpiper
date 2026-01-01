from typing import Protocol

from lotion import Lotion

from sandpiper.plan.query.routine_dto import RoutineDto
from sandpiper.shared.valueobject.task_chute_section import TaskChuteSection


class RoutineQuery(Protocol):
    def fetch(self) -> list[RoutineDto]: ...


class NotionRoutineQuery(RoutineQuery):
    def __init__(self):
        self.client = Lotion.get_instance()

    def fetch(self) -> list[RoutineDto]:
        items = self.client.retrieve_database("d21db86c92034ff498999d62354e8fe1")
        routines = []
        for item in items:
            start_date = item.get_date("次回実行日").start_date
            if not start_date:
                continue
            section_name = item.get_select("セクション").selected_name
            routine = RoutineDto(
                title=item.get_title_text(),
                date=start_date,
                section=TaskChuteSection(section_name),
            )
            routines.append(routine)
        return routines


if __name__ == "__main__":
    # uv run python -m src.sandpiper.todo.query.routine_query
    query = NotionRoutineQuery()
    routines = query.fetch()
    for routine in routines:
        print(routine)

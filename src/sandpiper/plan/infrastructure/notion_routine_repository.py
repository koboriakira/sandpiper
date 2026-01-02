from lotion import Lotion

from sandpiper.plan.domain.routine import Routine
from sandpiper.plan.domain.routine_cycle import RoutineCycle
from sandpiper.plan.domain.routine_repository import RoutineRepository
from sandpiper.shared.notion.notion_props import RoutineNextDate
from sandpiper.shared.valueobject.task_chute_section import TaskChuteSection


class NotionRoutineRepository(RoutineRepository):
    def __init__(self):
        self.client = Lotion.get_instance()

    def fetch(self) -> list[Routine]:
        items = self.client.retrieve_database("d21db86c92034ff498999d62354e8fe1")
        routines = []
        for item in items:
            start_date = item.get_date("次回実行日").start_date
            if not start_date:
                continue
            section_name = item.get_select("セクション").selected_name
            cycle = item.get_select("周期").selected_name
            routine = Routine(
                id=item.id,
                title=item.get_title_text(),
                date=start_date,
                section=TaskChuteSection(section_name),
                cycle=RoutineCycle(cycle),
            )
            routines.append(routine)
        return routines

    def update(self, routine: Routine) -> None:
        page = self.client.retrieve_page(routine.id)
        page.set_prop(RoutineNextDate.from_start_date(routine.date))
        self.client.update(page)

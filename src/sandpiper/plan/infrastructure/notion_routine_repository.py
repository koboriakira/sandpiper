from lotion import Lotion

from sandpiper.plan.domain.routine import Routine
from sandpiper.plan.domain.routine_cycle import RoutineCycle
from sandpiper.plan.domain.routine_repository import RoutineRepository
from sandpiper.shared.notion.databases import routine as routine_db
from sandpiper.shared.notion.databases.routine import RoutineNextDate
from sandpiper.shared.valueobject.task_chute_section import TaskChuteSection


class NotionRoutineRepository(RoutineRepository):
    def __init__(self) -> None:
        self.client = Lotion.get_instance()

    def fetch(self) -> list[Routine]:
        items = self.client.retrieve_database(routine_db.DATABASE_ID)
        routines = []
        for item in items:
            start_date = item.get_date("次回実行日").start_date
            if not start_date:
                continue
            section_name = item.get_select("セクション").selected_name
            cycle = item.get_select("周期").selected_name
            execution_time = item.get_number("実行時間").number
            context_prop = item.get_multi_select("コンテクスト")
            context = [v.name for v in context_prop.values] if context_prop else []
            sort_order_prop = item.get_text("並び順")
            sort_order = sort_order_prop.text if sort_order_prop else None
            scheduled_prop = item.get_date("予定")
            scheduled_start_time = scheduled_prop.start_datetime.time() if scheduled_prop.start_datetime else None
            scheduled_end_time = scheduled_prop.end_datetime.time() if scheduled_prop.end_datetime else None
            routine = Routine(
                id=item.id,
                title=item.get_title_text(),
                date=start_date,
                section=TaskChuteSection(section_name),
                cycle=RoutineCycle(cycle),
                execution_time=int(execution_time) if execution_time else None,
                block_children=item.block_children,
                context=context,
                sort_order=sort_order,
                scheduled_start_time=scheduled_start_time,
                scheduled_end_time=scheduled_end_time,
            )
            routines.append(routine)
        return routines

    def update(self, routine: Routine) -> None:
        page = self.client.retrieve_page(routine.id)
        page.set_prop(RoutineNextDate.from_start_date(routine.date))
        self.client.update(page)


if __name__ == "__main__":
    # uv run python -m src.sandpiper.plan.infrastructure.notion_routine_repository
    repo = NotionRoutineRepository()
    routines = repo.fetch()
    for routine in routines:
        print(routine)

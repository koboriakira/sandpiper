from datetime import timedelta

from sandpiper.plan.domain.todo import ToDo, ToDoKind
from sandpiper.shared.utils.date_utils import jst_now
from sandpiper.shared.valueobject.task_chute_section import TaskChuteSection


def next_todo_rule(title: str) -> ToDo | None:
    match title:
        case "洗濯":
            scheduled_datetime = jst_now() + timedelta(minutes=30)
            return ToDo(
                title="乾燥機に入れる",
                kind=ToDoKind.REPEAT,
                section=TaskChuteSection.new(scheduled_datetime),
                scheduled_start_datetime=scheduled_datetime,
            )
        case "乾燥機に入れる":
            scheduled_datetime = jst_now() + timedelta(hours=6)
            return ToDo(
                title="乾燥機から取り込む",
                kind=ToDoKind.REPEAT,
                section=TaskChuteSection.new(scheduled_datetime),
                scheduled_start_datetime=scheduled_datetime,
            )
        case "料理" | "朝食" | "昼食" | "夕食":
            scheduled_datetime = jst_now()
            return ToDo(
                title="食器洗い",
                kind=ToDoKind.REPEAT,
                section=TaskChuteSection.new(scheduled_datetime),
                scheduled_start_datetime=scheduled_datetime,
            )
        case "食器洗い":
            scheduled_datetime = jst_now() + timedelta(minutes=60)
            return ToDo(
                title="食器の片付け",
                kind=ToDoKind.REPEAT,
                section=TaskChuteSection.new(scheduled_datetime),
                scheduled_start_datetime=scheduled_datetime,
            )
        case "入浴":
            scheduled_datetime = jst_now()
            return ToDo(
                title="化粧水を塗る",
                kind=ToDoKind.REPEAT,
                section=TaskChuteSection.new(scheduled_datetime),
                scheduled_start_datetime=scheduled_datetime,
            )
        case _:
            return None

from datetime import timedelta

from sandpiper.plan.domain.todo import ToDo, ToDoKind
from sandpiper.shared.utils.date_utils import jst_now
from sandpiper.shared.valueobject.task_chute_section import TaskChuteSection


def next_todo_rule(title: str) -> ToDo | None:
    match title:
        case "洗濯":
            return ToDo(
                title="乾燥機に入れる",
                kind=ToDoKind.REPEAT,
                section=TaskChuteSection.new(jst_now() + timedelta(minutes=30)),
            )
        case "乾燥機に入れる":
            return ToDo(
                title="乾燥機から取り込む",
                kind=ToDoKind.REPEAT,
                section=TaskChuteSection.new(jst_now() + timedelta(hours=6)),
            )
        case _:
            return None

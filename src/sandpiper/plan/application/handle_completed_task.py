from datetime import timedelta

from sandpiper.plan.domain.todo import ToDo, ToDoKind
from sandpiper.plan.domain.todo_repository import TodoRepository
from sandpiper.shared.event.todo_completed import TodoCompleted
from sandpiper.shared.infrastructure.notice_messanger import NoticeMessanger
from sandpiper.shared.utils.date_utils import jst_now
from sandpiper.shared.valueobject.task_chute_section import TaskChuteSection


class HandleCompletedTask:
    def __init__(self, todo_repository: TodoRepository, default_notice_messanger: NoticeMessanger) -> None:
        self._todo_repository = todo_repository
        self._default_notice_messanger = default_notice_messanger

    def __call__(self, event: TodoCompleted) -> None:
        if event.title == "洗濯":
            next_todo = ToDo(
                title="乾燥機に入れる",
                kind=ToDoKind.REPEAT,
                section=TaskChuteSection.new(jst_now() + timedelta(minutes=30)),
            )
            self._todo_repository.save(next_todo)
        if event.title == "乾燥機に入れる":
            next_todo = ToDo(
                title="乾燥機から取り込む",
                kind=ToDoKind.REPEAT,
                section=TaskChuteSection.new(jst_now() + timedelta(hours=6)),
            )
            self._todo_repository.save(next_todo)
        if event.title in ["朝食", "昼食", "夕食"]:
            self._default_notice_messanger.send(f"サプリメントは摂取しましたか? ({event.title}完了通知より)")

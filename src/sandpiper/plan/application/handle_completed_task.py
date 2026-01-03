from sandpiper.plan.domain.next_todo_rule import next_todo_rule
from sandpiper.plan.domain.todo_repository import TodoRepository
from sandpiper.shared.event.todo_completed import TodoCompleted
from sandpiper.shared.infrastructure.commentator import Commentator
from sandpiper.shared.infrastructure.notice_messanger import NoticeMessanger


class HandleCompletedTask:
    def __init__(
        self, todo_repository: TodoRepository, default_notice_messanger: NoticeMessanger, commentator: Commentator
    ) -> None:
        self._todo_repository = todo_repository
        self._default_notice_messanger = default_notice_messanger
        self._commentator = commentator

    def __call__(self, event: TodoCompleted) -> None:
        # 次のToDoを作成
        next_todo = next_todo_rule(event.title)
        if next_todo is not None:
            self._todo_repository.save(next_todo)

        # 通知を送信
        if event.title in ["朝食", "昼食", "夕食"]:
            self._default_notice_messanger.send(f"サプリメントは摂取しましたか? ({event.title}完了通知より)")

        # プロジェクトにコメントを記録
        todo = self._todo_repository.find(event.page_id)
        if todo.project_page_id:
            self._commentator.comment(todo.project_page_id, f"「{event.title}」を実施しました")

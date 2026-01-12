from sandpiper.perform.query.incidental_task_query import IncidentalTaskQuery
from sandpiper.shared.event.todo_start_event import TodoStartEvent
from sandpiper.shared.infrastructure.slack_notice_messanger import SlackNoticeMessanger
from sandpiper.shared.valueobject.context import Context


class HandleTodoStartEvent:
    def __init__(
        self,
        incidental_task_query: IncidentalTaskQuery,
        slack_messanger: SlackNoticeMessanger,
    ) -> None:
        self._incidental_task_query = incidental_task_query
        self._slack_messanger = slack_messanger

    def __call__(self, event: TodoStartEvent) -> None:
        if event.context != Context.OUTING:
            return

        titles = self._incidental_task_query.fetch_by_context(Context.OUTING)

        if not titles:
            return

        titles_str = "、".join(titles)
        message = f"あわせて「{titles_str}」も実行してください"
        self._slack_messanger.send(message)

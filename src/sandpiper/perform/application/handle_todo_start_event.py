from sandpiper.plan.domain.someday_item import SomedayTiming
from sandpiper.plan.domain.someday_repository import SomedayRepository
from sandpiper.shared.event.todo_start_event import TodoStartEvent
from sandpiper.shared.infrastructure.slack_notice_messanger import SlackNoticeMessanger
from sandpiper.shared.valueobject.context import Context


class HandleTodoStartEvent:
    def __init__(
        self,
        someday_repository: SomedayRepository,
        slack_messanger: SlackNoticeMessanger,
    ) -> None:
        self._someday_repository = someday_repository
        self._slack_messanger = slack_messanger

    def __call__(self, event: TodoStartEvent) -> None:
        if event.context != Context.OUTING:
            return

        items = self._someday_repository.fetch_by_timing_and_context(
            timing=SomedayTiming.INCIDENTALLY,
            context=Context.OUTING.value,
        )

        if not items:
            return

        titles = "、".join(item.title for item in items)
        message = f"あわせて「{titles}」も実行してください"
        self._slack_messanger.send(message)

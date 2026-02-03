import asyncio
import logging

from sandpiper.shared.event.todo_started import TodoStarted
from sandpiper.shared.infrastructure.slack_notice_messanger import SlackNoticeMessanger

logger = logging.getLogger(__name__)


class ScheduleTaskEndNotification:
    """タスク開始時に所要時間後のSlack通知をスケジュールするハンドラー"""

    def __init__(self, slack_messanger: SlackNoticeMessanger) -> None:
        self._slack_messanger = slack_messanger

    def __call__(self, event: TodoStarted) -> None:
        if event.scheduled_duration is None:
            return

        duration_seconds = event.scheduled_duration.total_seconds()
        if duration_seconds <= 0:
            return

        task_name = event.name
        logger.info(
            "Scheduling task end notification for '%s' in %d seconds",
            task_name,
            duration_seconds,
        )

        # asyncio.create_taskで非同期タスクをスケジュール
        try:
            loop = asyncio.get_running_loop()
            # タスクをスケジュール(fire-and-forget)
            loop.create_task(  # noqa: RUF006
                self._send_notification_after_delay(task_name, duration_seconds)
            )
        except RuntimeError:
            # イベントループが実行されていない場合(テスト時など)は警告のみ
            logger.warning(
                "No running event loop. Skipping scheduled notification for '%s'",
                task_name,
            )

    async def _send_notification_after_delay(self, task_name: str, delay_seconds: float) -> None:
        """指定秒数後にSlack通知を送信"""
        await asyncio.sleep(delay_seconds)
        message = f"「{task_name}」の予定時間が終了しました"
        logger.info("Sending task end notification for '%s'", task_name)
        self._slack_messanger.send(message)

import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

import pytest

from sandpiper.perform.application.schedule_task_end_notification import ScheduleTaskEndNotification
from sandpiper.shared.event.todo_started import TodoStarted
from sandpiper.shared.infrastructure.slack_notice_messanger import SlackNoticeMessanger
from sandpiper.shared.valueobject.context import Context


class TestScheduleTaskEndNotification:
    def setup_method(self):
        self.mock_slack_messanger = Mock(spec=SlackNoticeMessanger)
        self.handler = ScheduleTaskEndNotification(self.mock_slack_messanger)

    def test_init(self):
        """初期化テスト"""
        slack_messanger = Mock(spec=SlackNoticeMessanger)
        handler = ScheduleTaskEndNotification(slack_messanger)
        assert handler._slack_messanger == slack_messanger

    def test_call_without_scheduled_duration(self):
        """scheduled_durationがNoneの場合は何もしない"""
        # Arrange
        event = TodoStarted(
            name="テストタスク",
            execution_time=datetime.now(),
            context=None,
            scheduled_duration=None,
        )

        # Act
        self.handler(event)

        # Assert
        self.mock_slack_messanger.send.assert_not_called()

    def test_call_with_zero_duration(self):
        """所要時間が0秒の場合は何もしない"""
        # Arrange
        event = TodoStarted(
            name="テストタスク",
            execution_time=datetime.now(),
            context=None,
            scheduled_duration=timedelta(seconds=0),
        )

        # Act
        self.handler(event)

        # Assert
        self.mock_slack_messanger.send.assert_not_called()

    def test_call_with_negative_duration(self):
        """所要時間が負の場合は何もしない"""
        # Arrange
        event = TodoStarted(
            name="テストタスク",
            execution_time=datetime.now(),
            context=None,
            scheduled_duration=timedelta(seconds=-100),
        )

        # Act
        self.handler(event)

        # Assert
        self.mock_slack_messanger.send.assert_not_called()

    def test_call_without_event_loop_logs_warning(self):
        """イベントループがない場合は警告をログに出力"""
        # Arrange
        event = TodoStarted(
            name="テストタスク",
            execution_time=datetime.now(),
            context=Context.WORK,
            scheduled_duration=timedelta(minutes=30),
        )

        # Act - イベントループがない状態で呼び出し
        with patch("sandpiper.perform.application.schedule_task_end_notification.logger") as mock_logger:
            self.handler(event)

        # Assert
        mock_logger.warning.assert_called_once()
        self.mock_slack_messanger.send.assert_not_called()


class TestScheduleTaskEndNotificationAsync:
    """非同期テスト"""

    def setup_method(self):
        self.mock_slack_messanger = Mock(spec=SlackNoticeMessanger)
        self.handler = ScheduleTaskEndNotification(self.mock_slack_messanger)

    @pytest.mark.asyncio
    async def test_send_notification_after_delay(self):
        """指定秒数後に通知が送信される"""
        # Arrange
        task_name = "テストタスク"
        delay_seconds = 0.1  # 100ms

        # Act
        await self.handler._send_notification_after_delay(task_name, delay_seconds)

        # Assert
        self.mock_slack_messanger.send.assert_called_once_with("「テストタスク」の予定時間が終了しました")

    @pytest.mark.asyncio
    async def test_call_schedules_task_with_event_loop(self):
        """イベントループが実行中の場合、タスクがスケジュールされる"""
        # Arrange
        event = TodoStarted(
            name="非同期テストタスク",
            execution_time=datetime.now(),
            context=None,
            scheduled_duration=timedelta(seconds=0.1),  # 100ms
        )

        # Act
        self.handler(event)

        # 少し待ってタスクが実行されるのを確認
        await asyncio.sleep(0.2)

        # Assert
        self.mock_slack_messanger.send.assert_called_once_with("「非同期テストタスク」の予定時間が終了しました")

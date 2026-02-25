"""cron実行時のSlack通知テスト"""

from unittest.mock import MagicMock

from sandpiper.shared.infrastructure.cron_notifier import CronNotifier


class TestCronNotifier:
    """CronNotifierのテスト"""

    def test_notify_success(self) -> None:
        """成功時のメッセージ送信"""
        mock_messanger = MagicMock()
        notifier = CronNotifier(messanger=mock_messanger)

        notifier.notify_success(command="sync-jira-to-project", summary="2件作成, 3件スキップ")

        mock_messanger.send.assert_called_once()
        message = mock_messanger.send.call_args[0][0]
        assert "sync-jira-to-project" in message
        assert "2件作成, 3件スキップ" in message

    def test_notify_failure(self) -> None:
        """失敗時のメッセージ送信"""
        mock_messanger = MagicMock()
        notifier = CronNotifier(messanger=mock_messanger)

        notifier.notify_failure(command="archive-old-todos", error="Connection timeout")

        mock_messanger.send.assert_called_once()
        message = mock_messanger.send.call_args[0][0]
        assert "archive-old-todos" in message
        assert "Connection timeout" in message

    def test_notify_success_without_summary(self) -> None:
        """サマリーなしの成功通知"""
        mock_messanger = MagicMock()
        notifier = CronNotifier(messanger=mock_messanger)

        notifier.notify_success(command="sync-jira-to-project")

        mock_messanger.send.assert_called_once()
        message = mock_messanger.send.call_args[0][0]
        assert "sync-jira-to-project" in message

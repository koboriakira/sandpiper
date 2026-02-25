"""cron定期実行の結果をSlack通知するユーティリティ"""

from sandpiper.shared.infrastructure.notice_messanger import NoticeMessanger


class CronNotifier:
    """cron実行結果のSlack通知を行うクラス"""

    def __init__(self, messanger: NoticeMessanger) -> None:
        self._messanger = messanger

    def notify_success(self, command: str, summary: str | None = None) -> None:
        """成功時の通知を送信する"""
        message = f"[cron] {command} 完了"
        if summary:
            message += f": {summary}"
        self._messanger.send(message)

    def notify_failure(self, command: str, error: str) -> None:
        """失敗時の通知を送信する"""
        message = f"[cron] {command} 失敗: {error}"
        self._messanger.send(message)

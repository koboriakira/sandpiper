import os
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from slack_sdk import WebClient


@dataclass(frozen=True)
class SlackMessage:
    """Slackメッセージを表すデータクラス"""

    ts: str
    text: str
    user: str | None
    timestamp: datetime

    @staticmethod
    def from_api_response(message: dict[str, Any]) -> "SlackMessage":
        """Slack APIレスポンスからSlackMessageを生成"""
        ts = message.get("ts", "")
        return SlackMessage(
            ts=ts,
            text=message.get("text", ""),
            user=message.get("user"),
            timestamp=datetime.fromtimestamp(float(ts)) if ts else datetime.now(),
        )


class SlackChannelReader:
    """Slackチャンネルの投稿を取得するクラス"""

    DEFAULT_CHANNEL_ID = "C02CVBZV0UB"
    DEFAULT_ENV_VAR = "SLACK_BOT_TOKEN_BUSINESS"

    def __init__(
        self,
        channel_id: str | None = None,
        token: str | None = None,
        env_var: str | None = None,
    ) -> None:
        self._channel_id = channel_id or self.DEFAULT_CHANNEL_ID
        env_var_name = env_var or self.DEFAULT_ENV_VAR
        self._client = WebClient(token=token or os.getenv(env_var_name))

    def fetch_messages(
        self,
        limit: int = 100,
        oldest: datetime | None = None,
        latest: datetime | None = None,
    ) -> list[SlackMessage]:
        """
        チャンネルの投稿を取得する

        Args:
            limit: 取得するメッセージ数の上限 (デフォルト: 100)
            oldest: この日時以降のメッセージを取得
            latest: この日時以前のメッセージを取得

        Returns:
            SlackMessageのリスト (新しい順)
        """
        kwargs: dict[str, Any] = {
            "channel": self._channel_id,
            "limit": limit,
        }

        if oldest:
            kwargs["oldest"] = str(oldest.timestamp())
        if latest:
            kwargs["latest"] = str(latest.timestamp())

        response = self._client.conversations_history(**kwargs)
        messages: list[dict[str, Any]] = response.get("messages", [])

        return [SlackMessage.from_api_response(msg) for msg in messages]

    def fetch_messages_for_date(self, target_date: datetime) -> list[SlackMessage]:
        """
        特定の日付の投稿を取得する

        Args:
            target_date: 取得対象の日付

        Returns:
            SlackMessageのリスト (新しい順)
        """
        start_of_day = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = target_date.replace(hour=23, minute=59, second=59, microsecond=999999)

        return self.fetch_messages(oldest=start_of_day, latest=end_of_day)

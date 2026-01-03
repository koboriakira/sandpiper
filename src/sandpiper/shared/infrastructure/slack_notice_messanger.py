import os

from slack_sdk import WebClient


class SlackNoticeMessanger:
    def __init__(self, channel_id: str, token: str | None = None) -> None:
        self._channel_id = channel_id
        self._client = WebClient(token=token or os.getenv("SLACK_BOT_TOKEN"))

    def send(self, message: str) -> None:
        text = f"<@U04PQMBCFNE> {message}"
        self._client.chat_postMessage(channel=self._channel_id, text=text)

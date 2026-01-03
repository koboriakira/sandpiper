"""GitHub API クライアント"""

import os
from collections.abc import Iterator
from datetime import datetime, timedelta

from github import Auth, Github
from github.Event import Event


class GitHubClient:
    """PyGithubのラッパークラス - GitHub API操作を提供"""

    def __init__(self, token: str | None = None) -> None:
        """
        GitHubクライアントを初期化

        Args:
            token: GitHub Personal Access Token (省略時は環境変数GITHUB_TOKENから取得)
        """
        self.token = token or os.getenv("GITHUB_TOKEN")
        if not self.token:
            msg = "GitHub token is required. Set GITHUB_TOKEN environment variable."
            raise ValueError(msg)

        auth = Auth.Token(self.token)
        self._github = Github(auth=auth)

    def get_user_events(self, username: str) -> Iterator[Event]:
        """
        ユーザーの公開イベントを取得

        Args:
            username: GitHubユーザー名

        Returns:
            イベントのイテレータ
        """
        user = self._github.get_user(username)
        return user.get_events()

    def filter_events_by_date(
        self,
        events: Iterator[Event],
        target_date: datetime,
    ) -> list[Event]:
        """
        指定日のイベントのみをフィルタリング

        Args:
            events: イベントのイテレータ
            target_date: 対象日付（UTC）

        Returns:
            フィルタリングされたイベントのリスト
        """
        start_of_day = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)

        filtered_events = []
        # 最新90件のイベントをチェック（GitHub APIの制限）
        for event in list(events)[:90]:
            event_date = event.created_at
            if start_of_day <= event_date < end_of_day:
                filtered_events.append(event)
            # 対象日より古いイベントが見つかったら終了
            elif event_date < start_of_day:
                break

        return filtered_events

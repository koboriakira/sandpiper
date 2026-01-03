"""GitHub活動ログ取得ユースケース"""

from datetime import UTC, datetime

from sandpiper.review.query.github_activity_dto import GitHubActivityDto
from sandpiper.review.query.github_activity_query import GitHubActivityQuery


class GetGitHubActivity:
    """GitHub活動ログ取得ユースケース(Application層)"""

    def __init__(self, github_activity_query: GitHubActivityQuery) -> None:
        """
        GetGitHubActivityを初期化

        Args:
            github_activity_query: GitHub活動クエリ
        """
        self.github_activity_query = github_activity_query

    def execute(
        self,
        username: str = "koboriakira",
        target_date: datetime | None = None,
    ) -> GitHubActivityDto:
        """
        GitHub活動ログを取得して返す

        Args:
            username: GitHubユーザー名(デフォルト: koboriakira)
            target_date: 対象日付(デフォルト: 今日)

        Returns:
            GitHub活動ログDTO
        """
        if target_date is None:
            target_date = datetime.now(UTC)

        return self.github_activity_query.fetch_daily_activity(
            username=username,
            target_date=target_date,
        )

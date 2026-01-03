"""GitHub活動ログクエリ"""

from datetime import datetime

from github.Event import Event

from sandpiper.review.query.github_activity_dto import (
    GitHubActivityDto,
    GitHubActivitySummary,
    GitHubCommitDto,
    GitHubIssueDto,
    GitHubPullRequestDto,
    GitHubReviewDto,
)
from sandpiper.shared.infrastructure.github_client import GitHubClient


class GitHubActivityQuery:
    """GitHub APIからデータを取得するクエリクラス（CQRS: 読み取り専門）"""

    def __init__(self, client: GitHubClient) -> None:
        """
        GitHubActivityQueryを初期化

        Args:
            client: GitHubクライアント
        """
        self.client = client

    def fetch_daily_activity(
        self,
        username: str,
        target_date: datetime,
    ) -> GitHubActivityDto:
        """
        指定日のGitHub活動を取得

        Args:
            username: GitHubユーザー名
            target_date: 対象日付（UTC）

        Returns:
            GitHub活動ログDTO
        """
        # ユーザーイベントを取得してフィルタリング
        events = self.client.get_user_events(username)
        filtered_events = self.client.filter_events_by_date(events, target_date)

        # イベントを種類別に分類
        commits: list[GitHubCommitDto] = []
        pull_requests: list[GitHubPullRequestDto] = []
        issues: list[GitHubIssueDto] = []
        reviews: list[GitHubReviewDto] = []

        for event in filtered_events:
            event_type = event.type
            repo_name = event.repo.name if event.repo else "N/A"

            if event_type == "PushEvent":
                commits.extend(self._extract_commits(event, repo_name))
            elif event_type == "PullRequestEvent":
                pr_dto = self._extract_pull_request(event, repo_name)
                if pr_dto:
                    pull_requests.append(pr_dto)
            elif event_type == "IssuesEvent":
                issue_dto = self._extract_issue(event, repo_name)
                if issue_dto:
                    issues.append(issue_dto)
            elif event_type == "PullRequestReviewEvent":
                review_dto = self._extract_review(event, repo_name)
                if review_dto:
                    reviews.append(review_dto)

        # サマリーを作成
        summary = GitHubActivitySummary(
            total_events=len(filtered_events),
            commits_count=len(commits),
            pull_requests_count=len(pull_requests),
            issues_count=len(issues),
            reviews_count=len(reviews),
        )

        return GitHubActivityDto(
            date=target_date.strftime("%Y-%m-%d"),
            username=username,
            commits=commits,
            pull_requests=pull_requests,
            issues=issues,
            reviews=reviews,
            summary=summary,
        )

    def _extract_commits(self, event: Event, repo_name: str) -> list[GitHubCommitDto]:
        """PushEventからコミット情報を抽出"""
        commits = []
        payload = event.payload

        if "commits" in payload:
            for commit in payload["commits"]:
                commits.append(
                    GitHubCommitDto(
                        sha=commit.get("sha", "")[:7],
                        message=commit.get("message", ""),
                        repo=repo_name,
                        committed_at=event.created_at,
                    )
                )

        return commits

    def _extract_pull_request(
        self,
        event: Event,
        repo_name: str,
    ) -> GitHubPullRequestDto | None:
        """PullRequestEventからプルリクエスト情報を抽出"""
        payload = event.payload

        if "pull_request" in payload:
            pr = payload["pull_request"]
            return GitHubPullRequestDto(
                number=pr.get("number", 0),
                title=pr.get("title", ""),
                action=payload.get("action", ""),
                repo=repo_name,
                created_at=event.created_at,
            )

        return None

    def _extract_issue(
        self,
        event: Event,
        repo_name: str,
    ) -> GitHubIssueDto | None:
        """IssuesEventからイシュー情報を抽出"""
        payload = event.payload

        if "issue" in payload:
            issue = payload["issue"]
            return GitHubIssueDto(
                number=issue.get("number", 0),
                title=issue.get("title", ""),
                action=payload.get("action", ""),
                repo=repo_name,
                created_at=event.created_at,
            )

        return None

    def _extract_review(
        self,
        event: Event,
        repo_name: str,
    ) -> GitHubReviewDto | None:
        """PullRequestReviewEventからレビュー情報を抽出"""
        payload = event.payload

        if "review" in payload and "pull_request" in payload:
            review = payload["review"]
            pr = payload["pull_request"]
            return GitHubReviewDto(
                pr_number=pr.get("number", 0),
                state=review.get("state", ""),
                repo=repo_name,
                created_at=event.created_at,
            )

        return None

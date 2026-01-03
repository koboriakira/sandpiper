"""GitHub活動ログのDTO(Data Transfer Object)"""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class GitHubCommitDto:
    """コミット情報"""

    sha: str
    message: str
    repo: str
    committed_at: datetime


@dataclass
class GitHubPullRequestDto:
    """プルリクエスト情報"""

    number: int
    title: str
    action: str  # opened, closed, merged, reopened
    repo: str
    created_at: datetime


@dataclass
class GitHubIssueDto:
    """イシュー情報"""

    number: int
    title: str
    action: str  # opened, closed, reopened
    repo: str
    created_at: datetime


@dataclass
class GitHubReviewDto:
    """プルリクエストレビュー情報"""

    pr_number: int
    state: str  # approved, commented, changes_requested
    repo: str
    created_at: datetime


@dataclass
class GitHubActivitySummary:
    """活動サマリー"""

    total_events: int
    commits_count: int
    pull_requests_count: int
    issues_count: int
    reviews_count: int


@dataclass
class GitHubActivityDto:
    """GitHub活動ログ"""

    date: str  # YYYY-MM-DD
    username: str
    commits: list[GitHubCommitDto]
    pull_requests: list[GitHubPullRequestDto]
    issues: list[GitHubIssueDto]
    reviews: list[GitHubReviewDto]
    summary: GitHubActivitySummary

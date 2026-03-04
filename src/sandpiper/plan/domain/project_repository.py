from typing import Protocol

from sandpiper.plan.domain.project import InsertedProject, Project
from sandpiper.shared.valueobject.todo_status_enum import ToDoStatusEnum


class ProjectRepository(Protocol):
    """プロジェクトリポジトリインターフェース"""

    def save(self, project: Project) -> InsertedProject:
        """プロジェクトを保存する"""
        ...

    def find(self, page_id: str) -> Project:
        """プロジェクトを取得する"""
        ...

    def find_by_jira_url(self, jira_url: str) -> InsertedProject | None:
        """Jira URLでプロジェクトを検索する"""
        ...

    def fetch_all_jira_urls(self) -> set[str]:
        """すべてのプロジェクトからJira URLの一覧を取得する"""
        ...

    def fetch_all(self) -> list[InsertedProject]:
        """すべてのプロジェクトを取得する"""
        ...

    def fetch_projects_with_jira_url(self) -> list[InsertedProject]:
        """Jira URLを持つすべてのプロジェクトを取得する"""
        ...

    def update_status(self, page_id: str, status: ToDoStatusEnum) -> None:
        """プロジェクトのステータスを更新する"""
        ...

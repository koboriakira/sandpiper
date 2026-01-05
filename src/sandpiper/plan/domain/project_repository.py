from typing import Protocol

from sandpiper.plan.domain.project import InsertedProject, Project


class ProjectRepository(Protocol):
    """プロジェクトリポジトリインターフェース"""

    def save(self, project: Project) -> InsertedProject:
        """プロジェクトを保存する"""
        ...

    def find(self, page_id: str) -> Project:
        """プロジェクトを取得する"""
        ...

from typing import Protocol

from sandpiper.plan.domain.project_task import InsertedProjectTask, ProjectTask


class ProjectTaskRepository(Protocol):
    """プロジェクトタスクリポジトリのインターフェース"""

    def save(self, project_task: ProjectTask) -> InsertedProjectTask: ...

    def start(self, page_id: str) -> bool:
        """プロジェクトタスクのステータスをInProgressに更新する

        Args:
            page_id: プロジェクトタスクのページID

        Returns:
            bool: 更新が実行された場合True、すでにInProgressの場合False
        """
        ...

from typing import Protocol

from lotion import Lotion  # type: ignore[import-untyped]

from sandpiper.plan.query.project_task_dto import ProjectTaskDto
from sandpiper.shared.notion.database_config import DatabaseId
from sandpiper.shared.valueobject.todo_status_enum import ToDoStatusEnum


class ProjectTaskQuery(Protocol):
    def fetch_undone_project_tasks(self) -> list[ProjectTaskDto]: ...


class NotionProjectTaskQuery(ProjectTaskQuery):
    def __init__(self) -> None:
        self.client = Lotion.get_instance()

    def fetch_undone_project_tasks(self) -> list[ProjectTaskDto]:
        items = self.client.retrieve_database(DatabaseId.PROJECT_TASK)
        project_dtos = []
        for item in items:
            status = ToDoStatusEnum(item.get_status("ステータス").status_name)
            if status == ToDoStatusEnum.DONE:
                continue
            # もしプロジェクトが紐づいていないタスクはスキップ
            project_relations = item.get_relation("プロジェクト").id_list
            if len(project_relations) == 0:
                continue

            is_next = item.get_checkbox("次やる").checked
            project_task = ProjectTaskDto(
                page_id=item.id,
                title=item.get_title_text(),
                status=status,
                project_page_id=project_relations[0],
                is_next=is_next,
                block_children=item.block_children,
            )
            project_dtos.append(project_task)
        return project_dtos

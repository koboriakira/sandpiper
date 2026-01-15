from typing import Protocol

from lotion import Lotion  # type: ignore[import-untyped]

from sandpiper.plan.query.project_task_dto import ProjectTaskDto
from sandpiper.shared.notion.databases import project_task as project_task_db
from sandpiper.shared.valueobject.todo_status_enum import ToDoStatusEnum


class ProjectTaskQuery(Protocol):
    def fetch_undone_project_tasks(self) -> list[ProjectTaskDto]: ...


class NotionProjectTaskQuery(ProjectTaskQuery):
    def __init__(self) -> None:
        self.client = Lotion.get_instance()

    def fetch_undone_project_tasks(self) -> list[ProjectTaskDto]:
        items = self.client.retrieve_database(project_task_db.DATABASE_ID)
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
            context_prop = item.get_multi_select("コンテクスト")
            context = [v.name for v in context_prop.values] if context_prop else []
            sort_order_prop = item.get_text("並び順")
            sort_order = sort_order_prop.text if sort_order_prop else None
            project_task = ProjectTaskDto(
                page_id=item.id,
                title=item.get_title_text(),
                status=status,
                project_page_id=project_relations[0],
                is_next=is_next,
                block_children=item.block_children,
                context=context,
                sort_order=sort_order,
            )
            project_dtos.append(project_task)
        return project_dtos

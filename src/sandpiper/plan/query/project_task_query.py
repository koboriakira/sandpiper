from typing import Protocol

from lotion import Lotion

from sandpiper.plan.query.project_task_dto import ProjectTaskDto
from sandpiper.shared.notion.databases import project as project_db
from sandpiper.shared.notion.databases import project_task as project_task_db
from sandpiper.shared.valueobject.todo_status_enum import ToDoStatusEnum


class ProjectTaskQuery(Protocol):
    def fetch_undone_project_tasks(self) -> list[ProjectTaskDto]: ...


class NotionProjectTaskQuery(ProjectTaskQuery):
    def __init__(self) -> None:
        self.client = Lotion.get_instance()

    def fetch_undone_project_tasks(self) -> list[ProjectTaskDto]:
        # プロジェクトのステータスを取得してキャッシュ
        project_status_map = self._fetch_project_status_map()

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

            # プロジェクトのステータスがToDoの場合はスキップ
            project_page_id = project_relations[0]
            project_status = project_status_map.get(project_page_id)
            if project_status == ToDoStatusEnum.TODO:
                continue

            is_next = item.get_checkbox("次やる").checked
            context_prop = item.get_multi_select("コンテクスト")
            context = [v.name for v in context_prop.values] if context_prop else []
            sort_order_prop = item.get_text("並び順")
            sort_order = sort_order_prop.text if sort_order_prop else None
            scheduled_date = item.get_date("予定").start_date
            project_task = ProjectTaskDto(
                page_id=item.id,
                title=item.get_title_text(),
                status=status,
                project_page_id=project_page_id,
                is_next=is_next,
                block_children=item.block_children,
                context=context,
                sort_order=sort_order,
                scheduled_date=scheduled_date,
            )
            project_dtos.append(project_task)
        return project_dtos

    def _fetch_project_status_map(self) -> dict[str, ToDoStatusEnum | None]:
        """プロジェクトIDとステータスのマップを取得する"""
        items = self.client.retrieve_database(project_db.DATABASE_ID)
        result: dict[str, ToDoStatusEnum | None] = {}
        for item in items:
            status_prop = item.get_status("ステータス")
            status = ToDoStatusEnum(status_prop.status_name) if status_prop.status_name else None
            result[item.id] = status
        return result

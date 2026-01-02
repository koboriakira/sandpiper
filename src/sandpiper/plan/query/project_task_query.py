from dataclasses import dataclass
from typing import Protocol

from lotion import Lotion

from sandpiper.plan.domain.todo import ToDo, ToDoKind
from sandpiper.shared.notion.database_config import DatabaseId
from sandpiper.shared.valueobject.todo_status_enum import ToDoStatusEnum


@dataclass
class ProjectTaskDto:
    page_id: str
    title: str
    status: ToDoStatusEnum
    project_page_id: str

    def to_todo_model(self) -> ToDo:
        return ToDo(
            title=self.title,
            section=None,
            kind=ToDoKind.PROJECT,
            project_page_id=self.project_page_id,
            project_task_page_id=self.page_id,
        )


class ProjectTaskQuery(Protocol):
    def fetch_undone_project_tasks(self) -> list[ProjectTaskDto]: ...


class NotionProjectTaskQuery(ProjectTaskQuery):
    def __init__(self):
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
            project_task = ProjectTaskDto(
                page_id=item.id,
                title=item.get_title_text(),
                status=status,
                project_page_id=project_relations[0],
            )
            project_dtos.append(project_task)
        return project_dtos

from datetime import datetime
from typing import Protocol

from lotion import BasePage, Lotion

from sandpiper.plan.domain.todo import ToDoKind
from sandpiper.review.query.done_todo_dto import DoneTodoDto
from sandpiper.shared.notion.database_config import DatabaseId
from sandpiper.shared.valueobject.todo_status_enum import ToDoStatusEnum


class TodoQuery(Protocol):
    def fetch_done_todos(self) -> list[DoneTodoDto]: ...


class NotionTodoQuery:
    def __init__(self) -> None:
        self.client = Lotion.get_instance()

    def fetch_done_todos(self) -> list[DoneTodoDto]:
        items = self.client.retrieve_database(DatabaseId.TODO)
        project_list = self.client.retrieve_database(DatabaseId.PROJECT)

        projects: dict[str, BasePage] = {}
        for project in project_list:
            projects[project.id] = project

        result = []
        for item in items:
            status = ToDoStatusEnum(item.get_status("ステータス").status_name)
            if status != ToDoStatusEnum.DONE:
                continue
            perform_range = item.get_date("実施期間")
            if perform_range.start is None or perform_range.end is None:
                continue
            kind_name = item.get_select("タスク種別").selected_name
            if not kind_name:
                continue

            kind = ToDoKind(kind_name)
            project_name = ""
            if kind == ToDoKind.PROJECT:
                # プロジェクトタスクの場合、関連するプロジェクトのステータスを確認
                project_page_id_list = item.get_relation("プロジェクト").id_list
                if not project_page_id_list:
                    continue
                project_page_id = project_page_id_list[0]
                project = projects[project_page_id]
                project_name = project.get_title_text()

            todo = DoneTodoDto(
                page_id=item.id,
                title=item.get_title_text(),
                perform_range=(
                    datetime.fromisoformat(perform_range.start),
                    datetime.fromisoformat(perform_range.end),
                ),
                kind=kind,
                project_name=project_name,
            )
            result.append(todo)
        return result

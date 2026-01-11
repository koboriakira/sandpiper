from typing import Protocol

from lotion import Lotion  # type: ignore[import-untyped]

from sandpiper.plan.domain.todo import ToDo, ToDoKind
from sandpiper.shared.notion.databases import todo as todo_db
from sandpiper.shared.valueobject.task_chute_section import TaskChuteSection
from sandpiper.shared.valueobject.todo_status_enum import ToDoStatusEnum


class TodoQuery(Protocol):
    def fetch_todos_not_is_today(self) -> list[ToDo]:
        """'今日中にやる'が無効かつTODOステータスのTODO一覧を取得する"""
        ...


class NotionTodoQuery(TodoQuery):
    def __init__(self) -> None:
        self.client = Lotion.get_instance()

    def fetch_todos_not_is_today(self) -> list[ToDo]:
        """'今日中にやる'が無効かつTODOステータスのTODO一覧を取得する"""
        items = self.client.retrieve_database(todo_db.DATABASE_ID)
        result: list[ToDo] = []
        for item in items:
            status = ToDoStatusEnum(item.get_status("ステータス").status_name)
            if status != ToDoStatusEnum.TODO:
                continue

            is_today = item.get_checkbox("今日中にやる").checked
            if is_today:
                continue

            section_select = item.get_select("セクション")
            kind_select = item.get_select("タスク種別")
            project_relations = item.get_relation("プロジェクト").id_list
            project_task_relations = item.get_relation("プロジェクトタスク").id_list
            execution_time = item.get_number("実行時間").number

            todo = ToDo(
                title=item.get_title_text(),
                kind=ToDoKind(kind_select.selected_name) if kind_select.selected_name else None,
                section=TaskChuteSection(section_select.selected_name) if section_select.selected_name else None,
                project_page_id=project_relations[0] if project_relations else None,
                project_task_page_id=project_task_relations[0] if project_task_relations else None,
                execution_time=int(execution_time) if execution_time else None,
            )
            result.append(todo)
        return result

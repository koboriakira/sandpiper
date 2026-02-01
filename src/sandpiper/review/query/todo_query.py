from datetime import date, datetime
from typing import Protocol

from lotion import BasePage, Lotion

from sandpiper.review.query.activity_log_item import ActivityLogItem, ActivityType
from sandpiper.shared.notion.databases import project as project_db
from sandpiper.shared.notion.databases import todo as todo_db
from sandpiper.shared.valueobject.todo_kind import ToDoKind
from sandpiper.shared.valueobject.todo_status_enum import ToDoStatusEnum


class TodoQuery(Protocol):
    def fetch_done_todos_by_date(self, target_date: date) -> list[ActivityLogItem]: ...


class NotionTodoQuery:
    def __init__(self) -> None:
        self.client = Lotion.get_instance()

    def fetch_done_todos_by_date(self, target_date: date) -> list[ActivityLogItem]:
        """指定された日付以降のDONEステータスのTODOを取得する"""
        items = self.client.retrieve_database(todo_db.DATABASE_ID)
        project_list = self.client.retrieve_database(project_db.DATABASE_ID)

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

            start_datetime = datetime.fromisoformat(perform_range.start)
            end_datetime = datetime.fromisoformat(perform_range.end)

            # 指定日付以降のタスクのみ抽出
            if start_datetime.date() < target_date:
                continue

            kind_name = item.get_select("タスク種別").selected_name
            if not kind_name:
                continue

            kind = ToDoKind(kind_name)
            project_name = ""
            if kind == ToDoKind.PROJECT:
                project_page_id_list = item.get_relation("プロジェクト").id_list
                if not project_page_id_list:
                    continue
                project_page_id = project_page_id_list[0]
                project = projects[project_page_id]
                project_name = project.get_title_text()

            activity = ActivityLogItem(
                activity_type=ActivityType.TODO,
                title=item.get_title_text(),
                start_datetime=start_datetime,
                end_datetime=end_datetime,
                kind=kind.value,
                project_name=project_name,
            )
            result.append(activity)
        return result

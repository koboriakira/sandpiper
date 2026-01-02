from datetime import datetime
from typing import Protocol

from lotion import Lotion

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
            todo = DoneTodoDto(
                page_id=item.id,
                title=item.get_title_text(),
                perform_range=(
                    datetime.fromisoformat(perform_range.start),
                    datetime.fromisoformat(perform_range.end),
                ),
                kind=kind,
            )
            result.append(todo)
        return result

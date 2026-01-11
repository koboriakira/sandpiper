from lotion import BasePage, Lotion, notion_database  # type: ignore[import-untyped]

from sandpiper.perform.domain.todo import ToDo
from sandpiper.shared.notion.databases import todo as todo_db
from sandpiper.shared.notion.databases.todo import (
    TodoLogDate,
    TodoName,
    TodoProjectTaskProp,
    TodoSection,
    TodoStatus,
)
from sandpiper.shared.valueobject.task_chute_section import TaskChuteSection
from sandpiper.shared.valueobject.todo_status_enum import ToDoStatusEnum


@notion_database(todo_db.DATABASE_ID)
class TodoPage(BasePage):  # type: ignore[misc]
    name: TodoName
    status: TodoStatus
    section: TodoSection | None = None
    log_date: TodoLogDate | None = None
    project_task_relation: TodoProjectTaskProp | None = None

    def to_domain(self) -> ToDo:
        section_name = self.get_select("セクション").selected_name
        log_start_datetime = self.get_date("実施期間").start_datetime
        log_end_datetime = self.get_date("実施期間").end_datetime
        project_task = self.get_relation("プロジェクトタスク").id_list
        return ToDo(
            id=self.id,
            title=self.get_title_text(),
            status=ToDoStatusEnum(self.get_status("ステータス").status_name),
            section=TaskChuteSection(section_name) if section_name else None,
            log_start_datetime=log_start_datetime,
            log_end_datetime=log_end_datetime,
            project_task_page_id=project_task[0] if project_task else None,
        )


class NotionTodoRepository:
    def __init__(self) -> None:
        self.client = Lotion.get_instance()

    def find(self, page_id: str) -> ToDo:
        page = self.client.retrieve_page(page_id, TodoPage)
        return page.to_domain()  # type: ignore[no-any-return]

    def save(self, todo: ToDo) -> None:
        print(f"Saving ToDo: {todo}")
        page = self.client.retrieve_page(todo.id, TodoPage)
        page.set_prop(TodoStatus.from_status_name(todo.status.value))
        page.set_prop(
            TodoLogDate.from_range(
                start=todo.log_start_datetime,
                end=todo.log_end_datetime,
            )
        )

        if todo.section:
            page.set_prop(TodoSection.from_name(todo.section.value))

        self.client.update(page)

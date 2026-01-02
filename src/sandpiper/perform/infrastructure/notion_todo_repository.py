from lotion import BasePage, Lotion, notion_database

from sandpiper.perform.domain.todo import ToDo
from sandpiper.shared.notion.database_config import DatabaseId
from sandpiper.shared.notion.notion_props import TodoLogDate, TodoName, TodoSection, TodoStatus
from sandpiper.shared.valueobject.task_chute_section import TaskChuteSection
from sandpiper.shared.valueobject.todo_status_enum import ToDoStatusEnum


@notion_database(DatabaseId.TODO)
class TodoPage(BasePage):
    name: TodoName
    status: TodoStatus
    section: TodoSection | None = None
    log_date: TodoLogDate | None = None

    def to_domain(self) -> ToDo:
        section_name = self.get_select("セクション").selected_name
        log_start_datetime = self.get_date("実施期間").start_datetime
        log_end_datetime = self.get_date("実施期間").end_datetime
        return ToDo(
            id=self.id,
            title=self.get_title_text(),
            status=ToDoStatusEnum(self.get_status("ステータス").status_name),
            section=TaskChuteSection(section_name) if section_name else None,
            log_start_datetime=log_start_datetime,
            log_end_datetime=log_end_datetime,
        )


class NotionTodoRepository:
    def __init__(self):
        self.client = Lotion.get_instance()

    def find(self, page_id: str) -> ToDo:
        page = self.client.retrieve_page(page_id, TodoPage)
        return page.to_domain()

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

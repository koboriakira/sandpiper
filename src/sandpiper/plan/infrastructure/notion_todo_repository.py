from typing import Any

from lotion import BasePage, Lotion, notion_database  # type: ignore[import-untyped]
from lotion.block.rich_text.rich_text_builder import RichTextBuilder  # type: ignore[import-untyped]

from sandpiper.plan.domain.todo import InsertedToDo, ToDo, ToDoKind, ToDoStatus
from sandpiper.shared.notion.block_service import get_block_service
from sandpiper.shared.notion.database_config import DatabaseId
from sandpiper.shared.notion.notion_props import (
    TodoExecutionTime,
    TodoKindProp,
    TodoName,
    TodoProjectProp,
    TodoProjectTaskProp,
    TodoSection,
    TodoStatus,
)
from sandpiper.shared.utils.date_utils import jst_today, jst_tommorow
from sandpiper.shared.valueobject.task_chute_section import TaskChuteSection


@notion_database(DatabaseId.TODO)
class TodoPage(BasePage):  # type: ignore[misc]
    name: TodoName
    status: TodoStatus
    kind: TodoKindProp | None = None
    section: TodoSection | None = None
    project_relation: TodoProjectProp | None = None
    project_task_relation: TodoProjectTaskProp | None = None

    @staticmethod
    def generate(todo: ToDo, options: dict[str, Any]) -> "TodoPage":
        properties = [
            TodoName.from_plain_text(todo.title),
            TodoStatus.from_status_name("ToDo"),
        ]
        t_kind = TodoKindProp.from_name(todo.kind.value) if todo.kind else None
        if t_kind:
            properties.append(t_kind)
        t_section = TodoSection.from_name(todo.section.value) if todo.section else None
        if t_section:
            properties.append(t_section)
        if todo.execution_time is not None:
            properties.append(TodoExecutionTime.from_num(todo.execution_time))
        if todo.project_page_id and todo.project_task_page_id:
            properties.append(TodoProjectProp.from_id(todo.project_page_id))
            properties.append(TodoProjectTaskProp.from_id(todo.project_task_page_id))
            start_day = jst_tommorow() if options.get("is_tomorrow") else jst_today()
            rich_text_builder = RichTextBuilder.create().add_text(todo.title).add_date_mention(start=start_day)
            properties.append(TodoName.from_rich_text(rich_text_builder.build()))
        return TodoPage.create(properties=properties)  # type: ignore[no-any-return]

    def to_domain(self) -> ToDo:
        section = self.get_select("セクション")
        kind = self.get_select("タスク種別")
        project = self.get_relation("プロジェクト").id_list
        project_task = self.get_relation("プロジェクトタスク").id_list
        execution_time = self.get_number("実行時間").number
        return ToDo(
            title=self.get_title_text(),
            kind=ToDoKind(kind.selected_name) if kind.selected_name else None,
            section=TaskChuteSection(section.selected_name) if section.selected_name else None,
            project_page_id=project[0] if project else None,
            project_task_page_id=project_task[0] if project_task else None,
            execution_time=int(execution_time) if execution_time else None,
        )


class NotionTodoRepository:
    def __init__(self) -> None:
        self.client = Lotion.get_instance()

    def save(self, todo: ToDo, options: dict[str, Any] | None = None) -> InsertedToDo:
        options = options or {}
        notion_todo = TodoPage.generate(todo, options=options)
        page = self.client.create_page(notion_todo)

        # ソースページIDが指定されている場合、ブロックをコピー
        source_page_id = options.get("source_page_id")
        if source_page_id:
            block_service = get_block_service()
            copied_count = block_service.copy_blocks(source_page_id, page.id)
            if copied_count > 0:
                print(f"Copied {copied_count} blocks from source page")

        return InsertedToDo(
            id=page.id,
            title=todo.title,
            section=todo.section,
            kind=todo.kind,
            execution_time=todo.execution_time,
        )

    def fetch(self) -> list[ToDo]:
        notion_pages = self.client.search_pages(
            cls=TodoPage, props=[TodoStatus.from_status_name(ToDoStatus.TODO.value)]
        )
        return [page.to_domain() for page in notion_pages]

    def find(self, page_id: str) -> ToDo:
        notion_page = self.client.retrieve_page(page_id, cls=TodoPage)
        return notion_page.to_domain()  # type: ignore[no-any-return]

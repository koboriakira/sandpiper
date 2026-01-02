from lotion import BasePage, Lotion, notion_database

from sandpiper.plan.domain.todo import InsertedToDo, ToDo, ToDoKind, ToDoStatus
from sandpiper.shared.notion.database_config import DatabaseId
from sandpiper.shared.notion.notion_props import TodoKind, TodoName, TodoSection, TodoStatus
from sandpiper.shared.valueobject.task_chute_section import TaskChuteSection


@notion_database(DatabaseId.TODO)
class TodoPage(BasePage):
    name: TodoName
    status: TodoStatus
    kind: TodoKind | None = None
    section: TodoSection | None = None

    @staticmethod
    def generate(todo: ToDo) -> "TodoPage":
        properties = [
            TodoName.from_plain_text(todo.title),
            TodoStatus.from_status_name("ToDo"),
        ]
        t_kind = TodoKind.from_name(todo.kind.value) if todo.kind else None
        if t_kind:
            properties.append(t_kind)
        t_section = TodoSection.from_name(todo.section.value) if todo.section else None
        if t_section:
            properties.append(t_section)
        return TodoPage.create(properties=properties)

    def to_domain(self) -> ToDo:
        section = self.get_select("セクション")
        kind = self.get_select("タスク種別")
        return ToDo(
            title=self.get_title_text(),
            kind=ToDoKind(kind.selected_name) if kind else None,
            section=TaskChuteSection(section.selected_name) if section else None,
        )


class NotionTodoRepository:
    def __init__(self):
        self.client = Lotion.get_instance()

    def save(self, todo: ToDo) -> InsertedToDo:
        notion_todo = TodoPage.generate(todo)
        page = self.client.create_page(notion_todo)
        return InsertedToDo(
            id=page.id,
            title=todo.title,
            section=todo.section,
            kind=todo.kind,
        )

    def fetch(self) -> list[ToDo]:
        notion_pages = self.client.search_pages(
            cls=TodoPage, props=[TodoStatus.from_status_name(ToDoStatus.TODO.value)]
        )
        return [page.to_domain() for page in notion_pages]

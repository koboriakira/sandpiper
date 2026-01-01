from lotion import BasePage, Lotion, notion_database, notion_prop
from lotion.properties import Select, Status, Title

from sandpiper.plan.domain.todo import ToDo, ToDoKind, ToDoStatus
from sandpiper.shared.notion.database_config import DatabaseId
from sandpiper.shared.valueobject.task_chute_section import TaskChuteSection


@notion_prop("名前")
class TodoName(Title): ...


@notion_prop("ステータス")
class TodoStatus(Status): ...


@notion_prop("タスク種別")
class TodoKind(Select): ...


@notion_prop("セクション")
class TodoSection(Select): ...


@notion_database(DatabaseId.TODO)
class TodoPage(BasePage):
    name: TodoName
    status: TodoStatus
    kind: TodoKind
    section: TodoSection

    @staticmethod
    def generate(todo: ToDo) -> "TodoPage":
        t_name = TodoName.from_plain_text(todo.title)
        t_status = TodoStatus.from_status_name(todo.status.value)
        t_kind = TodoKind.from_name(todo.kind.value)
        t_section = TodoSection.from_name(todo.section.value)
        return TodoPage.create(properties=[t_name, t_status, t_kind, t_section])

    def to_domain(self) -> ToDo:
        return ToDo(
            title=self.get_title_text(),
            status=ToDoStatus(self.status.status_name),
            kind=ToDoKind(self.kind.selected_name),
            section=TaskChuteSection(self.section.selected_name),
        )


class NotionTodoRepository:
    def __init__(self):
        self.client = Lotion.get_instance()

    def save(self, todo: ToDo) -> None:
        notion_todo = TodoPage.generate(todo)
        self.client.create_page(notion_todo)

    def fetch(self) -> list[ToDo]:
        notion_pages = self.client.search_pages(
            cls=TodoPage, props=[TodoStatus.from_status_name(ToDoStatus.TODO.value)]
        )
        return [page.to_domain() for page in notion_pages]

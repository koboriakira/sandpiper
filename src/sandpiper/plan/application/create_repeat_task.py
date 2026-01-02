from dataclasses import dataclass
from datetime import date

from sandpiper.plan.domain.todo import ToDo, ToDoKind, ToDoStatus
from sandpiper.plan.domain.todo_repository import TodoRepository
from sandpiper.plan.infrastructure.notion_todo_repository import NotionTodoRepository
from sandpiper.plan.query.routine_query import NotionRoutineQuery, RoutineQuery
from sandpiper.shared.utils.date_utils import jst_today


@dataclass
class CreateRepeatTask:
    routine_query: RoutineQuery
    todo_repository: TodoRepository

    def __init__(self):
        self.routine_query = NotionRoutineQuery()
        self.todo_repository = NotionTodoRepository()

    def execute(self, basis_date: date):
        # Create the main task
        routine_dto_list = self.routine_query.fetch()
        todos: list[ToDo] = self.todo_repository.fetch()
        todo_names = [todo.title for todo in todos]
        for routine_dto in routine_dto_list:
            # 今日の日付と一致するルーチンタスクのみ処理する
            if routine_dto.date != basis_date:
                continue

            # すでに同じタイトルのタスクが存在する場合はスキップする
            if routine_dto.title in todo_names:
                print(f"Skip creating repeat task (already exists): {routine_dto.title}")
                continue

            # Todoを作成する
            print(f"Create repeat task: {routine_dto.title}")
            todo = ToDo(
                title=routine_dto.title,
                status=ToDoStatus.TODO,
                section=routine_dto.section,
                kind=ToDoKind.REPEAT,
            )
            _inserted_todo = self.todo_repository.save(todo)


if __name__ == "__main__":
    # uv run python -m src.sandpiper.plan.application.create_repeat_task
    creator = CreateRepeatTask()
    creator.execute(jst_today())

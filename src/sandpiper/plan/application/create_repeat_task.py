from dataclasses import dataclass
from datetime import date

from sandpiper.plan.domain.todo import ToDo, ToDoKind
from sandpiper.plan.domain.todo_repository import TodoRepository
from sandpiper.plan.query.routine_query import RoutineQuery


@dataclass
class CreateRepeatTask:
    routine_query: RoutineQuery
    todo_repository: TodoRepository

    def __init__(self, routine_query: RoutineQuery, todo_repository: TodoRepository) -> None:
        self.routine_query = routine_query
        self.todo_repository = todo_repository

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
                section=routine_dto.section,
                kind=ToDoKind.REPEAT,
            )
            _inserted_todo = self.todo_repository.save(todo)

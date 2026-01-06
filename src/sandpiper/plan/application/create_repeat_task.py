from dataclasses import dataclass
from datetime import date

from sandpiper.plan.domain.routine_repository import RoutineRepository
from sandpiper.plan.domain.todo import ToDo, ToDoKind
from sandpiper.plan.domain.todo_repository import TodoRepository


@dataclass
class CreateRepeatTask:
    routine_repository: RoutineRepository
    todo_repository: TodoRepository

    def __init__(self, routine_repository: RoutineRepository, todo_repository: TodoRepository) -> None:
        self.routine_repository = routine_repository
        self.todo_repository = todo_repository

    def execute(self, basis_date: date) -> None:
        # Create the main task
        print("Creating repeat tasks...")
        routines = self.routine_repository.fetch()
        todos: list[ToDo] = self.todo_repository.fetch()
        todo_names = [todo.title for todo in todos]
        for routine in routines:
            # 今日の日付以前のルーチンタスクのみ処理する
            if routine.date > basis_date:
                print(f"Processing routine: {routine.title} (next date: {routine.date})")
                continue

            # すでに同じタイトルのタスクが存在する場合はスキップする
            if routine.title in todo_names:
                print(f"Skip creating repeat task (already exists): {routine.title}")
                continue

            # Todoを作成する
            print(f"Create repeat task: {routine.title}")
            todo = ToDo(
                title=routine.title,
                section=routine.section,
                kind=ToDoKind.REPEAT,
            )
            _inserted_todo = self.todo_repository.save(todo)

            # Routineの次回実行日を更新する
            routine = routine.next_cycle(basis_date=basis_date)
            print(f"Update routine next date: {routine.title} -> {routine.date}")
            self.routine_repository.update(routine)

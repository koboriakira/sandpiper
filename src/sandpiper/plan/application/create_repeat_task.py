from dataclasses import dataclass
from datetime import date

from sandpiper.plan.domain.routine_repository import RoutineRepository
from sandpiper.plan.domain.todo import ToDo, ToDoKind
from sandpiper.plan.domain.todo_repository import TodoRepository
from sandpiper.plan.query.todo_query import TodoQuery


@dataclass
class CreateRepeatTask:
    routine_repository: RoutineRepository
    todo_repository: TodoRepository
    todo_query: TodoQuery
    is_debug: bool = False

    def __init__(
        self,
        routine_repository: RoutineRepository,
        todo_repository: TodoRepository,
        todo_query: TodoQuery,
        is_debug: bool = False,
    ) -> None:
        self.routine_repository = routine_repository
        self.todo_repository = todo_repository
        self.todo_query = todo_query
        self.is_debug = is_debug

    def execute(self, basis_date: date) -> None:
        # Create the main task
        print("Creating repeat tasks...")
        routines = self.routine_repository.fetch()
        todos: list[ToDo] = self.todo_query.fetch_todos_not_is_today()
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

            # Todoを作成する(Routineのブロックもコピーする)
            print(f"Create repeat task: {routine.title}")
            todo = ToDo(
                title=routine.title,
                section=routine.section,
                kind=ToDoKind.REPEAT,
                execution_time=routine.execution_time,
                context=routine.context if routine.context else None,
                routine_page_id=routine.id,
                sort_order=routine.sort_order,
                scheduled_date=routine.scheduled_date,
            )
            if not self.is_debug:
                self.todo_repository.save(todo, {"block_children": routine.block_children})

            # Routineの次回実行日を更新する
            routine = routine.next_cycle(basis_date=basis_date)
            print(f"Update routine next date: {routine.title} -> {routine.date}")
            if not self.is_debug:
                self.routine_repository.update(routine)


if __name__ == "__main__":
    # uv run python -m src.sandpiper.plan.application.create_repeat_task
    from sandpiper.plan.infrastructure.notion_routine_repository import NotionRoutineRepository
    from sandpiper.plan.infrastructure.notion_todo_repository import NotionTodoRepository
    from sandpiper.plan.query.todo_query import NotionTodoQuery

    routine_repo = NotionRoutineRepository()
    todo_repo = NotionTodoRepository()
    todo_query = NotionTodoQuery()

    create_repeat_task = CreateRepeatTask(
        routine_repository=routine_repo,
        todo_repository=todo_repo,
        todo_query=todo_query,
        is_debug=True,
    )
    create_repeat_task.execute(basis_date=date.today())

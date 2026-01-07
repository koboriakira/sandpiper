from sandpiper.plan.domain.project_task_rule import group_next_project_tasks_by_project
from sandpiper.plan.domain.todo_repository import TodoRepository
from sandpiper.plan.query.project_task_query import ProjectTaskQuery


class CreateRepeatProjectTask:
    def __init__(self, project_task_query: ProjectTaskQuery, todo_repository: TodoRepository) -> None:
        self.project_task_query = project_task_query
        self.todo_repository = todo_repository

    def execute(self, is_tomorrow: bool) -> None:
        # 各プロジェクトごとにプロジェクトタスクをひとつ取得する
        project_task_dtos = self.project_task_query.fetch_undone_project_tasks()
        grouped_tasks = group_next_project_tasks_by_project(project_task_dtos)

        # プロジェクトタスクをToDoに変換(プロジェクトタスクのブロックもコピーする)
        for project_task in grouped_tasks.values():
            todo = project_task.to_todo_model()
            print(todo)
            # ToDoを保存
            options = {
                "is_tomorrow": is_tomorrow,
                "block_children": project_task.block_children,
            }
            _inserted_todo = self.todo_repository.save(todo, options)
            print(f"Create repeat project task: {todo.title}")

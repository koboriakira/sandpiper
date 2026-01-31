from datetime import date, timedelta

from sandpiper.plan.domain.project_task_rule import group_next_project_tasks_by_project
from sandpiper.plan.domain.todo_repository import TodoRepository
from sandpiper.plan.query.project_task_dto import ProjectTaskDto
from sandpiper.plan.query.project_task_query import ProjectTaskQuery
from sandpiper.shared.utils.date_utils import jst_today


class CreateRepeatProjectTask:
    def __init__(self, project_task_query: ProjectTaskQuery, todo_repository: TodoRepository) -> None:
        self.project_task_query = project_task_query
        self.todo_repository = todo_repository

    def execute(self, is_tomorrow: bool) -> None:
        # 各プロジェクトごとにプロジェクトタスクをひとつ取得する
        project_task_dtos = self.project_task_query.fetch_undone_project_tasks()

        # 基準日が土日の場合、仕事系プロジェクトのタスクを除外
        basis_date = jst_today() + timedelta(days=1) if is_tomorrow else jst_today()
        if self._is_weekend(basis_date):
            project_task_dtos = self._exclude_work_project_tasks(project_task_dtos)

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

    @staticmethod
    def _is_weekend(basis_date: date) -> bool:
        """基準日が土日かどうかを判定する"""
        # weekday(): 月曜=0, 火曜=1, ..., 土曜=5, 日曜=6
        return basis_date.weekday() >= 5

    @staticmethod
    def _exclude_work_project_tasks(
        project_task_dtos: list[ProjectTaskDto],
    ) -> list[ProjectTaskDto]:
        """仕事系プロジェクト(JiraにURLがあるプロジェクト)のタスクを除外する"""
        return [task for task in project_task_dtos if not task.is_work_project]

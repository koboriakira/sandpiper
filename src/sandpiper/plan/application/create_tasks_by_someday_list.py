from dataclasses import dataclass

from sandpiper.plan.domain.someday_item import SomedayItem
from sandpiper.plan.domain.someday_repository import SomedayRepository
from sandpiper.plan.domain.todo import ToDo, ToDoKind
from sandpiper.plan.domain.todo_repository import TodoRepository


@dataclass
class CreateTasksBySomedayListResult:
    """CreateTasksBySomedayListの実行結果"""

    created_count: int
    created_titles: list[str]


class CreateTasksBySomedayList:
    """サムデイリストからTODOを作成するアプリケーションサービス"""

    def __init__(
        self,
        someday_repository: SomedayRepository,
        todo_repository: TodoRepository,
    ) -> None:
        self._someday_repository = someday_repository
        self._todo_repository = todo_repository

    def execute(self) -> CreateTasksBySomedayListResult:
        """「明日やる」にチェックの入っているサムデイリストからTODOを作成し、元のアイテムを削除"""
        # 「明日やる」にチェックの入っているアイテムを取得
        tomorrow_items = self._someday_repository.fetch_tomorrow_items()

        created_titles: list[str] = []

        for item in tomorrow_items:
            # TODOを作成(タスク種別は「単発」)
            self._create_todo_from_someday_item(item)
            created_titles.append(item.title)

            # サムデイリストのアイテムを論理削除
            self._someday_repository.delete(item.id)

        return CreateTasksBySomedayListResult(
            created_count=len(created_titles),
            created_titles=created_titles,
        )

    def _create_todo_from_someday_item(self, item: SomedayItem) -> None:
        """サムデイアイテムからTODOを作成"""
        todo = ToDo(
            title=item.title,
            kind=ToDoKind.SINGLE,
        )
        self._todo_repository.save(todo)

"""明日のTODOリスト一括作成ユースケース

以下の処理をオーケストレーションする:
1. 未完了タスクに「今日中にやる」フラグを付ける
2. 論理削除されたページのアーカイブ
3. プロジェクトタスクからTODOを作成
4. ルーチンタスクからTODOを作成
5. サムデイリストからTODOを作成
6. カレンダーイベントからスケジュールタスクを作成
"""

from dataclasses import dataclass
from datetime import date, timedelta
from zoneinfo import ZoneInfo

from sandpiper.perform.application.mark_remaining_todos_as_today import MarkRemainingTodosAsToday
from sandpiper.plan.application.create_repeat_project_task import CreateRepeatProjectTask
from sandpiper.plan.application.create_repeat_task import CreateRepeatTask
from sandpiper.plan.application.create_schedule_tasks import CreateScheduleTasks
from sandpiper.plan.application.create_tasks_by_someday_list import CreateTasksBySomedayList
from sandpiper.shared.infrastructure.archive_deleted_pages import ArchiveDeletedPages

JST = ZoneInfo("Asia/Tokyo")


@dataclass
class PrepareTomorrowTodosResult:
    """実行結果"""

    target_label: str
    basis_date: date
    marked_as_today_count: int
    someday_created_count: int
    schedule_created_count: int

    @property
    def summary(self) -> str:
        details: list[str] = []
        if self.marked_as_today_count > 0:
            details.append(f"今日やるフラグ{self.marked_as_today_count}件")
        if self.someday_created_count > 0:
            details.append(f"サムデイリストから{self.someday_created_count}件")
        if self.schedule_created_count > 0:
            details.append(f"スケジュールから{self.schedule_created_count}件")
        message = f"{self.target_label}のTODOリストを作成しました"
        if details:
            message += f"({', '.join(details)})"
        return message


class PrepareTomorrowTodos:
    """明日(または今日)のTODOリストを一括作成するユースケース

    日本時間18:00〜23:59は「明日」、00:00〜17:59は「今日」として扱う。
    """

    def __init__(
        self,
        mark_remaining_todos_as_today: MarkRemainingTodosAsToday,
        create_repeat_project_task: CreateRepeatProjectTask,
        create_repeat_task: CreateRepeatTask,
        create_tasks_by_someday_list: CreateTasksBySomedayList,
        create_schedule_tasks: CreateScheduleTasks,
        archive_deleted_pages: ArchiveDeletedPages,
    ) -> None:
        self._mark_remaining_todos_as_today = mark_remaining_todos_as_today
        self._create_repeat_project_task = create_repeat_project_task
        self._create_repeat_task = create_repeat_task
        self._create_tasks_by_someday_list = create_tasks_by_someday_list
        self._create_schedule_tasks = create_schedule_tasks
        self._archive_deleted_pages = archive_deleted_pages

    def execute(self, is_tomorrow: bool, basis_date: date) -> PrepareTomorrowTodosResult:
        """TODOリストを一括作成する

        Args:
            is_tomorrow: 明日のTODOとして作成する場合True
            basis_date: ルーチンタスク・スケジュールの基準日

        Returns:
            PrepareTomorrowTodosResult: 処理結果
        """
        target_label = "明日" if is_tomorrow else "今日"

        # 1. 未完了タスクに「今日中にやる」フラグを付ける
        mark_result = self._mark_remaining_todos_as_today.execute()

        # 2. 論理削除されたページをアーカイブ
        self._archive_deleted_pages.execute()

        # 3. プロジェクトタスクからTODOを作成
        self._create_repeat_project_task.execute(is_tomorrow=is_tomorrow)

        # 4. ルーチンタスクからTODOを作成
        self._create_repeat_task.execute(basis_date=basis_date)

        # 5. サムデイリストからTODOを作成
        someday_result = self._create_tasks_by_someday_list.execute(basis_date=basis_date)

        # 6. カレンダーイベントからスケジュールタスクを作成
        schedule_result = self._create_schedule_tasks.execute(target_date=basis_date)

        return PrepareTomorrowTodosResult(
            target_label=target_label,
            basis_date=basis_date,
            marked_as_today_count=mark_result.marked_count,
            someday_created_count=someday_result.created_count,
            schedule_created_count=schedule_result.created_count,
        )

    @staticmethod
    def resolve_params_from_now(now_hour: int, today: date) -> tuple[bool, date]:
        """現在時刻から is_tomorrow と basis_date を決定する

        Args:
            now_hour: 現在時刻の時(0-23)
            today: 今日の日付

        Returns:
            (is_tomorrow, basis_date) のタプル
        """
        if 18 <= now_hour <= 23:
            return True, today + timedelta(days=1)
        return False, today

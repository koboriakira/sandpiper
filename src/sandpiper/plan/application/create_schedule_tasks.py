"""スケジュールタスク作成ユースケース

カレンダーイベントからスケジュールタスクをTODOリストに作成する
"""

from dataclasses import dataclass
from datetime import date

from sandpiper.plan.domain.todo import ToDo, ToDoKind
from sandpiper.plan.domain.todo_repository import TodoRepository
from sandpiper.plan.query.calendar_event_query import CalendarEventQuery
from sandpiper.plan.query.todo_query import TodoQuery


@dataclass
class CreateScheduleTasksResult:
    """スケジュールタスク作成の結果"""

    created_count: int


@dataclass
class CreateScheduleTasks:
    """カレンダーイベントからスケジュールタスクを作成するユースケース

    指定された日付のカレンダーイベントを取得し、
    それぞれをスケジュールタスクとしてTODOリストに登録する。

    - 実行時間: 開始時刻と終了時刻から計算(分単位)
    - 並び順: 開始時刻をHH:mm形式で記録
    - タスク種別: スケジュール
    """

    calendar_event_query: CalendarEventQuery
    todo_repository: TodoRepository
    todo_query: TodoQuery
    is_debug: bool = False

    def __init__(
        self,
        calendar_event_query: CalendarEventQuery,
        todo_repository: TodoRepository,
        todo_query: TodoQuery,
        is_debug: bool = False,
    ) -> None:
        self.calendar_event_query = calendar_event_query
        self.todo_repository = todo_repository
        self.todo_query = todo_query
        self.is_debug = is_debug

    def execute(self, target_date: date) -> CreateScheduleTasksResult:
        """指定日のカレンダーイベントからスケジュールタスクを作成する

        Args:
            target_date: スケジュールタスクを作成する対象の日付

        Returns:
            作成結果(作成されたタスク数を含む)
        """
        print(f"Creating schedule tasks for {target_date}...")

        # カレンダーイベントを取得
        events = self.calendar_event_query.fetch_events_by_date(target_date)
        if not events:
            print("No calendar events found for the specified date.")
            return CreateScheduleTasksResult(created_count=0)

        # 既存のTODOを取得して重複チェック用のタイトルリストを作成
        existing_todos = self.todo_query.fetch_todos_not_is_today()
        existing_todo_names = [todo.title for todo in existing_todos]

        created_count = 0
        for event in events:
            # すでに同じタイトルのタスクが存在する場合はスキップ
            if event.name in existing_todo_names:
                print(f"Skip creating schedule task (already exists): {event.name}")
                continue

            # 実行時間を計算
            execution_time = event.calculate_duration_minutes()

            # 並び順を取得(HH:mm形式、JST)
            sort_order = event.get_sort_order()

            # セクションを取得(JST開始時刻から判定)
            section = event.get_section()

            # 予定時刻を取得(JST変換後)
            scheduled_start = event.get_start_datetime_jst()
            scheduled_end = event.get_end_datetime_jst()

            # TODOを作成
            todo = ToDo(
                title=event.name,
                kind=ToDoKind.SCHEDULE,
                section=section,
                execution_time=execution_time,
                sort_order=sort_order,
                scheduled_start_datetime=scheduled_start,
                scheduled_end_datetime=scheduled_end,
            )

            print(
                f"Create schedule task: {event.name} (section: {section.value}, duration: {execution_time}min, sort: {sort_order})"
            )

            if not self.is_debug:
                self.todo_repository.save(todo)
                created_count += 1

        return CreateScheduleTasksResult(created_count=created_count)

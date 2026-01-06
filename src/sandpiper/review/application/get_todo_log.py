from datetime import date

from sandpiper.review.query.activity_log_item import ActivityLogItem
from sandpiper.review.query.calendar_query import CalendarQuery
from sandpiper.review.query.done_todo_dto import DoneTodoDto
from sandpiper.review.query.todo_query import TodoQuery


class GetTodoLog:
    def __init__(self, todo_query: TodoQuery, calendar_query: CalendarQuery | None = None) -> None:
        self.todo_query = todo_query
        self.calendar_query = calendar_query

    def execute(self) -> list[DoneTodoDto]:
        """従来のメソッド: 全てのDONE TODOを取得"""
        done_todos = self.todo_query.fetch_done_todos()

        # perform_range.0の昇順でソート
        done_todos.sort(key=lambda dto: dto.perform_range[0])
        return done_todos

    def execute_with_date(self, target_date: date) -> list[ActivityLogItem]:
        """指定日付以降のDONE TODOとカレンダーイベントを取得"""
        # 指定日付以降のDONE TODOを取得
        todos = self.todo_query.fetch_done_todos_by_date(target_date)

        # カレンダーイベントを取得(カレンダークエリが設定されている場合)
        calendar_events: list[ActivityLogItem] = []
        if self.calendar_query:
            calendar_events = self.calendar_query.fetch_events_by_date(target_date)

        # TODOとカレンダーイベントを統合
        all_items = todos + calendar_events

        # 開始時刻の昇順でソート
        all_items.sort(key=lambda item: item.start_datetime)
        return all_items

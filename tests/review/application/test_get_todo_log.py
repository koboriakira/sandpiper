from datetime import date, datetime
from unittest.mock import Mock

import pytest

from sandpiper.review.application.get_todo_log import GetTodoLog
from sandpiper.review.query.activity_log_item import ActivityLogItem, ActivityType
from sandpiper.review.query.calendar_query import CalendarQuery
from sandpiper.review.query.todo_query import TodoQuery


class TestGetTodoLog:
    def setup_method(self):
        self.mock_todo_query = Mock(spec=TodoQuery)
        self.mock_calendar_query = Mock(spec=CalendarQuery)
        self.get_todo_log = GetTodoLog(self.mock_todo_query, self.mock_calendar_query)

    def test_init(self):
        """GetTodoLogの初期化をテスト"""
        todo_query = Mock(spec=TodoQuery)
        calendar_query = Mock(spec=CalendarQuery)

        get_todo_log = GetTodoLog(todo_query, calendar_query)

        assert get_todo_log.todo_query == todo_query
        assert get_todo_log.calendar_query == calendar_query

    def test_execute_empty_result(self):
        """空の結果でのexecuteをテスト"""
        target_date = date(2024, 1, 15)
        self.mock_todo_query.fetch_done_todos_by_date.return_value = []
        self.mock_calendar_query.fetch_events_by_date.return_value = []

        result = self.get_todo_log.execute(target_date)

        assert result == []
        self.mock_todo_query.fetch_done_todos_by_date.assert_called_once_with(target_date)
        self.mock_calendar_query.fetch_events_by_date.assert_called_once_with(target_date)

    def test_execute_todos_only(self):
        """TODOのみ取得をテスト"""
        target_date = date(2024, 1, 15)
        todo_item = ActivityLogItem(
            activity_type=ActivityType.TODO,
            title="テストタスク",
            start_datetime=datetime(2024, 1, 15, 10, 0),
            end_datetime=datetime(2024, 1, 15, 11, 0),
            kind="SINGLE",
            project_name="",
        )
        self.mock_todo_query.fetch_done_todos_by_date.return_value = [todo_item]
        self.mock_calendar_query.fetch_events_by_date.return_value = []

        result = self.get_todo_log.execute(target_date)

        assert len(result) == 1
        assert result[0] == todo_item

    def test_execute_calendar_only(self):
        """カレンダーのみ取得をテスト"""
        target_date = date(2024, 1, 15)
        calendar_item = ActivityLogItem(
            activity_type=ActivityType.CALENDAR,
            title="会議",
            start_datetime=datetime(2024, 1, 15, 14, 0),
            end_datetime=datetime(2024, 1, 15, 15, 0),
            category="仕事",
        )
        self.mock_todo_query.fetch_done_todos_by_date.return_value = []
        self.mock_calendar_query.fetch_events_by_date.return_value = [calendar_item]

        result = self.get_todo_log.execute(target_date)

        assert len(result) == 1
        assert result[0] == calendar_item

    def test_execute_mixed_sorted_by_start_time(self):
        """TODOとカレンダーが開始時刻でソートされることをテスト"""
        target_date = date(2024, 1, 15)
        todo1 = ActivityLogItem(
            activity_type=ActivityType.TODO,
            title="朝のタスク",
            start_datetime=datetime(2024, 1, 15, 9, 0),
            end_datetime=datetime(2024, 1, 15, 10, 0),
            kind="SINGLE",
        )
        calendar1 = ActivityLogItem(
            activity_type=ActivityType.CALENDAR,
            title="午後の会議",
            start_datetime=datetime(2024, 1, 15, 14, 0),
            end_datetime=datetime(2024, 1, 15, 15, 0),
            category="仕事",
        )
        todo2 = ActivityLogItem(
            activity_type=ActivityType.TODO,
            title="昼のタスク",
            start_datetime=datetime(2024, 1, 15, 12, 0),
            end_datetime=datetime(2024, 1, 15, 13, 0),
            kind="PROJECT",
            project_name="テストプロジェクト",
        )

        self.mock_todo_query.fetch_done_todos_by_date.return_value = [todo2, todo1]  # 逆順
        self.mock_calendar_query.fetch_events_by_date.return_value = [calendar1]

        result = self.get_todo_log.execute(target_date)

        assert len(result) == 3
        assert result[0] == todo1  # 9:00
        assert result[1] == todo2  # 12:00
        assert result[2] == calendar1  # 14:00

    def test_execute_query_raises_exception(self):
        """todo_queryでの例外処理をテスト"""
        target_date = date(2024, 1, 15)
        self.mock_todo_query.fetch_done_todos_by_date.side_effect = Exception("Query failed")

        with pytest.raises(Exception, match="Query failed"):
            self.get_todo_log.execute(target_date)

        self.mock_todo_query.fetch_done_todos_by_date.assert_called_once_with(target_date)

    def test_execute_preserve_original_data(self):
        """元のDTOデータが保持されることをテスト"""
        target_date = date(2024, 1, 15)
        original_todo = ActivityLogItem(
            activity_type=ActivityType.TODO,
            title="データ保持テスト",
            start_datetime=datetime(2024, 1, 15, 9, 30),
            end_datetime=datetime(2024, 1, 15, 10, 45),
            kind="REPEAT",
            project_name="保持プロジェクト",
        )
        self.mock_todo_query.fetch_done_todos_by_date.return_value = [original_todo]
        self.mock_calendar_query.fetch_events_by_date.return_value = []

        result = self.get_todo_log.execute(target_date)

        returned_todo = result[0]
        assert returned_todo.title == "データ保持テスト"
        assert returned_todo.start_datetime == datetime(2024, 1, 15, 9, 30)
        assert returned_todo.end_datetime == datetime(2024, 1, 15, 10, 45)
        assert returned_todo.kind == "REPEAT"
        assert returned_todo.project_name == "保持プロジェクト"

    def test_execute_same_start_time_multiple_items(self):
        """同じ開始時刻の複数アイテムでのテスト"""
        target_date = date(2024, 1, 15)
        same_start_time = datetime(2024, 1, 15, 10, 0)

        todo1 = ActivityLogItem(
            activity_type=ActivityType.TODO,
            title="タスクA",
            start_datetime=same_start_time,
            end_datetime=datetime(2024, 1, 15, 11, 0),
            kind="SINGLE",
        )
        calendar1 = ActivityLogItem(
            activity_type=ActivityType.CALENDAR,
            title="会議A",
            start_datetime=same_start_time,
            end_datetime=datetime(2024, 1, 15, 12, 0),
            category="仕事",
        )

        self.mock_todo_query.fetch_done_todos_by_date.return_value = [todo1]
        self.mock_calendar_query.fetch_events_by_date.return_value = [calendar1]

        result = self.get_todo_log.execute(target_date)

        assert len(result) == 2
        # 同じ開始時刻の場合、安定ソートされる(元の順序が保持される)
        assert result[0] == todo1
        assert result[1] == calendar1

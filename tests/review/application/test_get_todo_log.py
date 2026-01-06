from datetime import date, datetime
from unittest.mock import Mock

import pytest

from sandpiper.plan.domain.todo import ToDoKind
from sandpiper.review.application.get_todo_log import GetTodoLog
from sandpiper.review.query.activity_log_item import ActivityLogItem, ActivityType
from sandpiper.review.query.calendar_query import CalendarQuery
from sandpiper.review.query.done_todo_dto import DoneTodoDto
from sandpiper.review.query.todo_query import TodoQuery


class TestGetTodoLog:
    def setup_method(self):
        self.mock_query = Mock(spec=TodoQuery)
        self.get_todo_log = GetTodoLog(self.mock_query)

    def test_init(self):
        """GetTodoLogの初期化をテスト"""
        query = Mock(spec=TodoQuery)

        get_todo_log = GetTodoLog(query)

        assert get_todo_log.todo_query == query

    def test_execute_empty_result(self):
        """空の結果でのexecuteをテスト"""
        # Arrange
        self.mock_query.fetch_done_todos.return_value = []

        # Act
        result = self.get_todo_log.execute()

        # Assert
        assert result == []
        self.mock_query.fetch_done_todos.assert_called_once()

    def test_execute_single_todo(self):
        """単一ToDoでのexecuteをテスト"""
        # Arrange
        todo_dto = DoneTodoDto(
            page_id="test-1",
            title="テストタスク",
            perform_range=(datetime(2024, 1, 15, 10, 0), datetime(2024, 1, 15, 11, 0)),
            kind=ToDoKind.SINGLE,
            project_name="テストプロジェクト",
        )
        self.mock_query.fetch_done_todos.return_value = [todo_dto]

        # Act
        result = self.get_todo_log.execute()

        # Assert
        assert len(result) == 1
        assert result[0] == todo_dto
        self.mock_query.fetch_done_todos.assert_called_once()

    def test_execute_multiple_todos_sorted_by_perform_range(self):
        """複数ToDoのperform_range[0]でソートされることをテスト"""
        # Arrange - 意図的に順序を逆にして作成
        todo1 = DoneTodoDto(
            page_id="test-1",
            title="後のタスク",
            perform_range=(
                datetime(2024, 1, 15, 14, 0),  # 後の時刻
                datetime(2024, 1, 15, 15, 0),
            ),
            kind=ToDoKind.SINGLE,
            project_name="",
        )
        todo2 = DoneTodoDto(
            page_id="test-2",
            title="前のタスク",
            perform_range=(
                datetime(2024, 1, 15, 10, 0),  # 前の時刻
                datetime(2024, 1, 15, 11, 0),
            ),
            kind=ToDoKind.PROJECT,
            project_name="プロジェクトA",
        )
        todo3 = DoneTodoDto(
            page_id="test-3",
            title="中間のタスク",
            perform_range=(
                datetime(2024, 1, 15, 12, 0),  # 中間の時刻
                datetime(2024, 1, 15, 13, 0),
            ),
            kind=ToDoKind.INTERRUPTION,
            project_name="",
        )

        # 順序を逆にして設定
        self.mock_query.fetch_done_todos.return_value = [todo1, todo2, todo3]

        # Act
        result = self.get_todo_log.execute()

        # Assert
        assert len(result) == 3
        # perform_range[0]の昇順でソートされていることを確認
        assert result[0] == todo2  # 10:00 (最も早い)
        assert result[1] == todo3  # 12:00 (中間)
        assert result[2] == todo1  # 14:00 (最も遅い)

        self.mock_query.fetch_done_todos.assert_called_once()

    def test_execute_same_start_time_multiple_todos(self):
        """同じ開始時刻の複数ToDoでのテスト"""
        # Arrange - 同じ開始時刻の3つのタスク
        same_start_time = datetime(2024, 1, 15, 10, 0)

        todo1 = DoneTodoDto(
            page_id="test-1",
            title="タスクA",
            perform_range=(same_start_time, datetime(2024, 1, 15, 11, 0)),
            kind=ToDoKind.SINGLE,
            project_name="",
        )
        todo2 = DoneTodoDto(
            page_id="test-2",
            title="タスクB",
            perform_range=(same_start_time, datetime(2024, 1, 15, 12, 0)),
            kind=ToDoKind.PROJECT,
            project_name="プロジェクト",
        )

        self.mock_query.fetch_done_todos.return_value = [todo1, todo2]

        # Act
        result = self.get_todo_log.execute()

        # Assert
        assert len(result) == 2
        # 同じ開始時刻の場合、安定ソートされる(元の順序が保持される)
        assert result[0] == todo1
        assert result[1] == todo2

        self.mock_query.fetch_done_todos.assert_called_once()

    def test_execute_query_raises_exception(self):
        """todo_queryでの例外処理をテスト"""
        # Arrange
        self.mock_query.fetch_done_todos.side_effect = Exception("Query failed")

        # Act & Assert
        with pytest.raises(Exception, match="Query failed"):
            self.get_todo_log.execute()

        self.mock_query.fetch_done_todos.assert_called_once()

    def test_execute_preserve_original_data(self):
        """元のDTOデータが保持されることをテスト"""
        # Arrange
        original_todo = DoneTodoDto(
            page_id="preserve-test",
            title="データ保持テスト",
            perform_range=(datetime(2024, 1, 15, 9, 30), datetime(2024, 1, 15, 10, 45)),
            kind=ToDoKind.REPEAT,
            project_name="保持プロジェクト",
        )
        self.mock_query.fetch_done_todos.return_value = [original_todo]

        # Act
        result = self.get_todo_log.execute()

        # Assert
        returned_todo = result[0]
        assert returned_todo.page_id == "preserve-test"
        assert returned_todo.title == "データ保持テスト"
        assert returned_todo.perform_range == (datetime(2024, 1, 15, 9, 30), datetime(2024, 1, 15, 10, 45))
        assert returned_todo.kind == ToDoKind.REPEAT
        assert returned_todo.project_name == "保持プロジェクト"

        self.mock_query.fetch_done_todos.assert_called_once()

    def test_execute_cross_day_sorting(self):
        """日をまたぐタスクのソートをテスト"""
        # Arrange
        todo_today = DoneTodoDto(
            page_id="today",
            title="今日のタスク",
            perform_range=(
                datetime(2024, 1, 15, 23, 0),  # 今日の深夜
                datetime(2024, 1, 16, 1, 0),
            ),
            kind=ToDoKind.SINGLE,
            project_name="",
        )
        todo_tomorrow = DoneTodoDto(
            page_id="tomorrow",
            title="明日のタスク",
            perform_range=(
                datetime(2024, 1, 16, 9, 0),  # 翌日の朝
                datetime(2024, 1, 16, 10, 0),
            ),
            kind=ToDoKind.PROJECT,
            project_name="翌日プロジェクト",
        )

        # 順序を逆にして設定
        self.mock_query.fetch_done_todos.return_value = [todo_tomorrow, todo_today]

        # Act
        result = self.get_todo_log.execute()

        # Assert
        assert len(result) == 2
        assert result[0] == todo_today  # 15日23:00 (先)
        assert result[1] == todo_tomorrow  # 16日9:00 (後)

        self.mock_query.fetch_done_todos.assert_called_once()


class TestGetTodoLogWithDate:
    def setup_method(self):
        self.mock_todo_query = Mock(spec=TodoQuery)
        self.mock_calendar_query = Mock(spec=CalendarQuery)
        self.get_todo_log = GetTodoLog(self.mock_todo_query, self.mock_calendar_query)

    def test_init_with_calendar_query(self):
        """GetTodoLogのカレンダークエリ付き初期化をテスト"""
        todo_query = Mock(spec=TodoQuery)
        calendar_query = Mock(spec=CalendarQuery)

        get_todo_log = GetTodoLog(todo_query, calendar_query)

        assert get_todo_log.todo_query == todo_query
        assert get_todo_log.calendar_query == calendar_query

    def test_init_without_calendar_query(self):
        """GetTodoLogのカレンダークエリなし初期化をテスト"""
        todo_query = Mock(spec=TodoQuery)

        get_todo_log = GetTodoLog(todo_query)

        assert get_todo_log.todo_query == todo_query
        assert get_todo_log.calendar_query is None

    def test_execute_with_date_empty_result(self):
        """日付指定で空の結果をテスト"""
        target_date = date(2024, 1, 15)
        self.mock_todo_query.fetch_done_todos_by_date.return_value = []
        self.mock_calendar_query.fetch_events_by_date.return_value = []

        result = self.get_todo_log.execute_with_date(target_date)

        assert result == []
        self.mock_todo_query.fetch_done_todos_by_date.assert_called_once_with(target_date)
        self.mock_calendar_query.fetch_events_by_date.assert_called_once_with(target_date)

    def test_execute_with_date_todos_only(self):
        """日付指定でTODOのみ取得をテスト"""
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

        result = self.get_todo_log.execute_with_date(target_date)

        assert len(result) == 1
        assert result[0] == todo_item

    def test_execute_with_date_calendar_only(self):
        """日付指定でカレンダーのみ取得をテスト"""
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

        result = self.get_todo_log.execute_with_date(target_date)

        assert len(result) == 1
        assert result[0] == calendar_item

    def test_execute_with_date_mixed_sorted_by_start_time(self):
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

        result = self.get_todo_log.execute_with_date(target_date)

        assert len(result) == 3
        assert result[0] == todo1  # 9:00
        assert result[1] == todo2  # 12:00
        assert result[2] == calendar1  # 14:00

    def test_execute_with_date_without_calendar_query(self):
        """カレンダークエリなしでの日付指定をテスト"""
        get_todo_log = GetTodoLog(self.mock_todo_query)  # カレンダークエリなし
        target_date = date(2024, 1, 15)
        todo_item = ActivityLogItem(
            activity_type=ActivityType.TODO,
            title="タスク",
            start_datetime=datetime(2024, 1, 15, 10, 0),
            end_datetime=datetime(2024, 1, 15, 11, 0),
            kind="SINGLE",
        )
        self.mock_todo_query.fetch_done_todos_by_date.return_value = [todo_item]

        result = get_todo_log.execute_with_date(target_date)

        assert len(result) == 1
        assert result[0] == todo_item

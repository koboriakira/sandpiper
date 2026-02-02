from datetime import date, datetime, timedelta, timezone
from unittest.mock import Mock

from sandpiper.plan.application.create_schedule_tasks import (
    CreateScheduleTasks,
    CreateScheduleTasksResult,
)
from sandpiper.plan.domain.todo import ToDo, ToDoKind
from sandpiper.plan.domain.todo_repository import TodoRepository
from sandpiper.plan.query.calendar_event_query import CalendarEventDto, CalendarEventQuery
from sandpiper.plan.query.todo_query import TodoQuery
from sandpiper.shared.valueobject.task_chute_section import TaskChuteSection

# テスト用タイムゾーン
JST = timezone(timedelta(hours=9))


class TestCalendarEventDto:
    def test_calculate_duration_minutes_one_hour(self):
        """1時間のイベントの実行時間計算"""
        event = CalendarEventDto(
            name="会議",
            start_datetime=datetime(2024, 3, 20, 10, 0),
            end_datetime=datetime(2024, 3, 20, 11, 0),
        )
        assert event.calculate_duration_minutes() == 60

    def test_calculate_duration_minutes_thirty_minutes(self):
        """30分のイベントの実行時間計算"""
        event = CalendarEventDto(
            name="打ち合わせ",
            start_datetime=datetime(2024, 3, 20, 14, 0),
            end_datetime=datetime(2024, 3, 20, 14, 30),
        )
        assert event.calculate_duration_minutes() == 30

    def test_calculate_duration_minutes_two_hours(self):
        """2時間のイベントの実行時間計算"""
        event = CalendarEventDto(
            name="ワークショップ",
            start_datetime=datetime(2024, 3, 20, 9, 0),
            end_datetime=datetime(2024, 3, 20, 11, 0),
        )
        assert event.calculate_duration_minutes() == 120

    def test_get_sort_order_morning_utc(self):
        """UTC午前のイベントの並び順取得(JST変換後)"""
        # UTC 00:30 → JST 09:30
        event = CalendarEventDto(
            name="朝会",
            start_datetime=datetime(2024, 3, 20, 0, 30),
            end_datetime=datetime(2024, 3, 20, 1, 0),
        )
        assert event.get_sort_order() == "09:30"

    def test_get_sort_order_afternoon_utc(self):
        """UTC午後のイベントの並び順取得(JST変換後)"""
        # UTC 05:15 → JST 14:15
        event = CalendarEventDto(
            name="午後の会議",
            start_datetime=datetime(2024, 3, 20, 5, 15),
            end_datetime=datetime(2024, 3, 20, 6, 0),
        )
        assert event.get_sort_order() == "14:15"

    def test_get_sort_order_midnight_utc(self):
        """UTC深夜のイベントの並び順取得(JST変換後)"""
        # UTC 15:05 → JST 翌日00:05
        event = CalendarEventDto(
            name="深夜作業",
            start_datetime=datetime(2024, 3, 20, 15, 5),
            end_datetime=datetime(2024, 3, 20, 16, 0),
        )
        assert event.get_sort_order() == "00:05"

    def test_get_section_morning(self):
        """午前セクションの判定"""
        # UTC 00:00 → JST 09:00 → A_07_10セクション
        event = CalendarEventDto(
            name="朝会",
            start_datetime=datetime(2024, 3, 20, 0, 0),
            end_datetime=datetime(2024, 3, 20, 1, 0),
        )
        assert event.get_section() == TaskChuteSection.A_07_10

    def test_get_section_afternoon(self):
        """午後セクションの判定"""
        # UTC 05:00 → JST 14:00 → C_13_17セクション
        event = CalendarEventDto(
            name="午後の会議",
            start_datetime=datetime(2024, 3, 20, 5, 0),
            end_datetime=datetime(2024, 3, 20, 6, 0),
        )
        assert event.get_section() == TaskChuteSection.C_13_17

    def test_get_section_evening(self):
        """夕方セクションの判定"""
        # UTC 10:00 → JST 19:00 → E_19_22セクション
        event = CalendarEventDto(
            name="夕方の会議",
            start_datetime=datetime(2024, 3, 20, 10, 0),
            end_datetime=datetime(2024, 3, 20, 11, 0),
        )
        assert event.get_section() == TaskChuteSection.E_19_22

    def test_get_end_datetime_jst_utc(self):
        """UTC終了時刻のJST変換"""
        # UTC 06:00 → JST 15:00
        event = CalendarEventDto(
            name="会議",
            start_datetime=datetime(2024, 3, 20, 5, 0),
            end_datetime=datetime(2024, 3, 20, 6, 0),
        )
        result = event.get_end_datetime_jst()
        assert result == datetime(2024, 3, 20, 15, 0)

    def test_get_end_datetime_jst_with_timezone(self):
        """タイムゾーン付き終了時刻のJST変換"""
        # UTC 06:00 (timezone aware) → JST 15:00
        event = CalendarEventDto(
            name="会議",
            start_datetime=datetime(2024, 3, 20, 5, 0, tzinfo=timezone.utc),  # noqa: UP017
            end_datetime=datetime(2024, 3, 20, 6, 0, tzinfo=timezone.utc),  # noqa: UP017
        )
        result = event.get_end_datetime_jst()
        assert result.hour == 15
        assert result.minute == 0


class TestCreateScheduleTasks:
    def setup_method(self):
        self.mock_calendar_event_query = Mock(spec=CalendarEventQuery)
        self.mock_todo_repository = Mock(spec=TodoRepository)
        self.mock_todo_query = Mock(spec=TodoQuery)
        self.service = CreateScheduleTasks(
            calendar_event_query=self.mock_calendar_event_query,
            todo_repository=self.mock_todo_repository,
            todo_query=self.mock_todo_query,
        )

    def test_execute_with_no_events(self):
        """カレンダーイベントがない場合のテスト"""
        # Arrange
        self.mock_calendar_event_query.fetch_events_by_date.return_value = []
        target_date = date(2024, 3, 20)

        # Act
        result = self.service.execute(target_date=target_date)

        # Assert
        assert result.created_count == 0
        self.mock_todo_repository.save.assert_not_called()

    def test_execute_with_single_event(self):
        """1つのカレンダーイベントがある場合のテスト"""
        # Arrange: UTC 01:00 → JST 10:00
        event = CalendarEventDto(
            name="チームミーティング",
            start_datetime=datetime(2024, 3, 20, 1, 0),
            end_datetime=datetime(2024, 3, 20, 2, 0),
        )
        self.mock_calendar_event_query.fetch_events_by_date.return_value = [event]
        self.mock_todo_query.fetch_todos_not_is_today.return_value = []
        target_date = date(2024, 3, 20)

        # Act
        result = self.service.execute(target_date=target_date)

        # Assert
        assert result.created_count == 1
        self.mock_todo_repository.save.assert_called_once()

        saved_todo = self.mock_todo_repository.save.call_args[0][0]
        assert isinstance(saved_todo, ToDo)
        assert saved_todo.title == "チームミーティング"
        assert saved_todo.kind == ToDoKind.SCHEDULE
        assert saved_todo.execution_time == 60
        assert saved_todo.sort_order == "10:00"
        assert saved_todo.section == TaskChuteSection.B_10_13

    def test_execute_with_multiple_events(self):
        """複数のカレンダーイベントがある場合のテスト"""
        # Arrange
        events = [
            CalendarEventDto(
                name="朝会",
                start_datetime=datetime(2024, 3, 20, 9, 0),
                end_datetime=datetime(2024, 3, 20, 9, 30),
            ),
            CalendarEventDto(
                name="ランチミーティング",
                start_datetime=datetime(2024, 3, 20, 12, 0),
                end_datetime=datetime(2024, 3, 20, 13, 0),
            ),
            CalendarEventDto(
                name="夕会",
                start_datetime=datetime(2024, 3, 20, 17, 0),
                end_datetime=datetime(2024, 3, 20, 17, 30),
            ),
        ]
        self.mock_calendar_event_query.fetch_events_by_date.return_value = events
        self.mock_todo_query.fetch_todos_not_is_today.return_value = []
        target_date = date(2024, 3, 20)

        # Act
        result = self.service.execute(target_date=target_date)

        # Assert
        assert result.created_count == 3
        assert self.mock_todo_repository.save.call_count == 3

        # 全てのTODOがSCHEDULE種別であることを確認
        for call_args in self.mock_todo_repository.save.call_args_list:
            saved_todo = call_args[0][0]
            assert saved_todo.kind == ToDoKind.SCHEDULE

    def test_execute_skips_existing_todos(self):
        """既存のTODOと同じタイトルのイベントはスキップされる"""
        # Arrange
        event = CalendarEventDto(
            name="既存の会議",
            start_datetime=datetime(2024, 3, 20, 10, 0),
            end_datetime=datetime(2024, 3, 20, 11, 0),
        )
        self.mock_calendar_event_query.fetch_events_by_date.return_value = [event]

        existing_todo = ToDo(title="既存の会議", kind=ToDoKind.SCHEDULE)
        self.mock_todo_query.fetch_todos_not_is_today.return_value = [existing_todo]
        target_date = date(2024, 3, 20)

        # Act
        result = self.service.execute(target_date=target_date)

        # Assert
        assert result.created_count == 0
        self.mock_todo_repository.save.assert_not_called()

    def test_execute_creates_only_new_events(self):
        """既存のTODOがあっても新規イベントは作成される"""
        # Arrange
        events = [
            CalendarEventDto(
                name="既存の会議",
                start_datetime=datetime(2024, 3, 20, 10, 0),
                end_datetime=datetime(2024, 3, 20, 11, 0),
            ),
            CalendarEventDto(
                name="新規の会議",
                start_datetime=datetime(2024, 3, 20, 14, 0),
                end_datetime=datetime(2024, 3, 20, 15, 0),
            ),
        ]
        self.mock_calendar_event_query.fetch_events_by_date.return_value = events

        existing_todo = ToDo(title="既存の会議", kind=ToDoKind.SCHEDULE)
        self.mock_todo_query.fetch_todos_not_is_today.return_value = [existing_todo]
        target_date = date(2024, 3, 20)

        # Act
        result = self.service.execute(target_date=target_date)

        # Assert
        assert result.created_count == 1
        self.mock_todo_repository.save.assert_called_once()

        saved_todo = self.mock_todo_repository.save.call_args[0][0]
        assert saved_todo.title == "新規の会議"

    def test_todo_has_correct_execution_time(self):
        """TODOの実行時間が正しく計算されることを確認"""
        # Arrange
        event = CalendarEventDto(
            name="45分の会議",
            start_datetime=datetime(2024, 3, 20, 10, 0),
            end_datetime=datetime(2024, 3, 20, 10, 45),
        )
        self.mock_calendar_event_query.fetch_events_by_date.return_value = [event]
        self.mock_todo_query.fetch_todos_not_is_today.return_value = []
        target_date = date(2024, 3, 20)

        # Act
        self.service.execute(target_date=target_date)

        # Assert
        saved_todo = self.mock_todo_repository.save.call_args[0][0]
        assert saved_todo.execution_time == 45

    def test_todo_has_correct_sort_order(self):
        """TODOの並び順が正しく設定されることを確認"""
        # Arrange: UTC 05:30 → JST 14:30
        event = CalendarEventDto(
            name="午後の会議",
            start_datetime=datetime(2024, 3, 20, 5, 30),
            end_datetime=datetime(2024, 3, 20, 6, 30),
        )
        self.mock_calendar_event_query.fetch_events_by_date.return_value = [event]
        self.mock_todo_query.fetch_todos_not_is_today.return_value = []
        target_date = date(2024, 3, 20)

        # Act
        self.service.execute(target_date=target_date)

        # Assert
        saved_todo = self.mock_todo_repository.save.call_args[0][0]
        assert saved_todo.sort_order == "14:30"
        assert saved_todo.section == TaskChuteSection.C_13_17

    def test_todo_has_scheduled_datetime(self):
        """TODOに予定開始・終了時刻が設定されることを確認"""
        # Arrange: UTC 05:30 → JST 14:30, UTC 06:30 → JST 15:30
        event = CalendarEventDto(
            name="予定付き会議",
            start_datetime=datetime(2024, 3, 20, 5, 30),
            end_datetime=datetime(2024, 3, 20, 6, 30),
        )
        self.mock_calendar_event_query.fetch_events_by_date.return_value = [event]
        self.mock_todo_query.fetch_todos_not_is_today.return_value = []
        target_date = date(2024, 3, 20)

        # Act
        self.service.execute(target_date=target_date)

        # Assert
        saved_todo = self.mock_todo_repository.save.call_args[0][0]
        # 開始時刻: UTC 05:30 → JST 14:30
        assert saved_todo.scheduled_start_datetime == datetime(2024, 3, 20, 14, 30)
        # 終了時刻: UTC 06:30 → JST 15:30
        assert saved_todo.scheduled_end_datetime == datetime(2024, 3, 20, 15, 30)


class TestCreateScheduleTasksResult:
    def test_result_creation(self):
        """結果オブジェクトの作成をテスト"""
        result = CreateScheduleTasksResult(created_count=3)
        assert result.created_count == 3

    def test_result_with_zero_count(self):
        """作成数ゼロの結果オブジェクトをテスト"""
        result = CreateScheduleTasksResult(created_count=0)
        assert result.created_count == 0

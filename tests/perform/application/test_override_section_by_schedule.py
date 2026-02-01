from datetime import datetime
from unittest.mock import Mock

import pytest

from sandpiper.perform.application.override_section_by_schedule import (
    OverrideSectionBulkResult,
    OverrideSectionBySchedule,
    OverrideSectionResult,
)
from sandpiper.perform.domain.todo import ToDo
from sandpiper.perform.domain.todo_repository import TodoRepository
from sandpiper.shared.valueobject.task_chute_section import TaskChuteSection
from sandpiper.shared.valueobject.todo_status_enum import ToDoStatusEnum


class TestOverrideSectionBySchedule:
    def setup_method(self) -> None:
        self.mock_repository = Mock(spec=TodoRepository)
        self.use_case = OverrideSectionBySchedule(self.mock_repository)

    def test_init(self) -> None:
        """OverrideSectionByScheduleの初期化をテスト"""
        repository = Mock(spec=TodoRepository)
        use_case = OverrideSectionBySchedule(repository)
        assert use_case._todo_repository == repository

    def test_execute_success_morning_section(self) -> None:
        """朝の時間帯(7-10時)での正常な実行をテスト"""
        # Arrange
        page_id = "test-page-id"
        # naive datetimeはUTCとみなされ+9時間される
        # 結果的にJST 8:30にするにはUTC 23:30(前日)を設定
        # しかしテストをシンプルにするため、Mockを使う
        mock_todo = Mock(spec=ToDo)
        mock_todo.id = page_id
        mock_todo.title = "朝の予定タスク"
        mock_todo.section = TaskChuteSection.C_13_17
        # JST 8:30 = UTC 23:30 (前日)
        mock_todo.scheduled_start_datetime = datetime(2024, 3, 19, 23, 30)
        self.mock_repository.find.return_value = mock_todo

        # Act
        result = self.use_case.execute(page_id)

        # Assert
        assert isinstance(result, OverrideSectionResult)
        assert result.page_id == page_id
        assert result.title == "朝の予定タスク"
        assert result.old_section == TaskChuteSection.C_13_17
        assert result.new_section == TaskChuteSection.A_07_10
        self.mock_repository.find.assert_called_once_with(page_id)
        self.mock_repository.update_section.assert_called_once_with(page_id, TaskChuteSection.A_07_10)

    def test_execute_success_afternoon_section(self) -> None:
        """午後の時間帯(13-17時)での正常な実行をテスト"""
        # Arrange
        page_id = "test-page-id"
        mock_todo = Mock(spec=ToDo)
        mock_todo.id = page_id
        mock_todo.title = "午後の予定タスク"
        mock_todo.section = TaskChuteSection.A_07_10
        # JST 14:00 = UTC 05:00
        mock_todo.scheduled_start_datetime = datetime(2024, 3, 20, 5, 0)
        self.mock_repository.find.return_value = mock_todo

        # Act
        result = self.use_case.execute(page_id)

        # Assert
        assert result.new_section == TaskChuteSection.C_13_17
        self.mock_repository.update_section.assert_called_once_with(page_id, TaskChuteSection.C_13_17)

    def test_execute_success_evening_section(self) -> None:
        """夜の時間帯(19-22時)での正常な実行をテスト"""
        # Arrange
        page_id = "test-page-id"
        mock_todo = Mock(spec=ToDo)
        mock_todo.id = page_id
        mock_todo.title = "夜の予定タスク"
        mock_todo.section = None
        # JST 20:30 = UTC 11:30
        mock_todo.scheduled_start_datetime = datetime(2024, 3, 20, 11, 30)
        self.mock_repository.find.return_value = mock_todo

        # Act
        result = self.use_case.execute(page_id)

        # Assert
        assert result.old_section is None
        assert result.new_section == TaskChuteSection.E_19_22

    def test_execute_success_late_night_section(self) -> None:
        """深夜の時間帯(22-24時)での正常な実行をテスト"""
        # Arrange
        page_id = "test-page-id"
        mock_todo = Mock(spec=ToDo)
        mock_todo.id = page_id
        mock_todo.title = "深夜の予定タスク"
        mock_todo.section = None
        # JST 23:00 = UTC 14:00
        mock_todo.scheduled_start_datetime = datetime(2024, 3, 20, 14, 0)
        self.mock_repository.find.return_value = mock_todo

        # Act
        result = self.use_case.execute(page_id)

        # Assert
        assert result.new_section == TaskChuteSection.F_22_24

    def test_execute_success_early_morning_section(self) -> None:
        """早朝の時間帯(0-7時)での正常な実行をテスト"""
        # Arrange
        page_id = "test-page-id"
        mock_todo = Mock(spec=ToDo)
        mock_todo.id = page_id
        mock_todo.title = "早朝の予定タスク"
        mock_todo.section = None
        # JST 3:00 = UTC 18:00 (前日)
        mock_todo.scheduled_start_datetime = datetime(2024, 3, 19, 18, 0)
        self.mock_repository.find.return_value = mock_todo

        # Act
        result = self.use_case.execute(page_id)

        # Assert
        assert result.new_section == TaskChuteSection.G_24_07

    def test_execute_raises_error_when_no_scheduled_datetime(self) -> None:
        """予定開始日時が設定されていない場合にValueErrorがスローされることをテスト"""
        # Arrange
        page_id = "test-page-id"
        mock_todo = ToDo(
            id=page_id,
            title="予定なしタスク",
            status=ToDoStatusEnum.TODO,
            section=None,
            scheduled_start_datetime=None,  # 予定開始日時なし
        )
        self.mock_repository.find.return_value = mock_todo

        # Act & Assert
        with pytest.raises(ValueError, match="予定開始日時が設定されていません"):
            self.use_case.execute(page_id)

        self.mock_repository.find.assert_called_once_with(page_id)
        self.mock_repository.update_section.assert_not_called()

    def test_execute_repository_find_raises_exception(self) -> None:
        """repository.find()で例外が発生した場合のテスト"""
        # Arrange
        page_id = "test-page-id"
        self.mock_repository.find.side_effect = Exception("Todo not found")

        # Act & Assert
        with pytest.raises(Exception, match="Todo not found"):
            self.use_case.execute(page_id)

        self.mock_repository.find.assert_called_once_with(page_id)
        self.mock_repository.update_section.assert_not_called()

    def test_execute_repository_update_raises_exception(self) -> None:
        """repository.update_section()で例外が発生した場合のテスト"""
        # Arrange
        page_id = "test-page-id"
        scheduled_datetime = datetime(2024, 3, 20, 10, 0)
        mock_todo = ToDo(
            id=page_id,
            title="テストタスク",
            status=ToDoStatusEnum.TODO,
            section=None,
            scheduled_start_datetime=scheduled_datetime,
        )
        self.mock_repository.find.return_value = mock_todo
        self.mock_repository.update_section.side_effect = Exception("Update failed")

        # Act & Assert
        with pytest.raises(Exception, match="Update failed"):
            self.use_case.execute(page_id)

        self.mock_repository.find.assert_called_once_with(page_id)
        self.mock_repository.update_section.assert_called_once()

    def test_execute_returns_formatted_datetime_string(self) -> None:
        """結果に正しくフォーマットされた日時文字列が含まれることをテスト"""
        # Arrange
        page_id = "test-page-id"
        scheduled_datetime = datetime(2024, 3, 20, 15, 45)
        mock_todo = ToDo(
            id=page_id,
            title="テストタスク",
            status=ToDoStatusEnum.TODO,
            section=None,
            scheduled_start_datetime=scheduled_datetime,
        )
        self.mock_repository.find.return_value = mock_todo

        # Act
        result = self.use_case.execute(page_id)

        # Assert
        # JSTオフセットが加算される (naive datetimeはUTCとみなす)
        expected_hour = (15 + 9) % 24  # 24時を超える場合
        if 15 + 9 >= 24:
            assert "00:45" in result.scheduled_start_datetime_str
        else:
            assert f"{expected_hour:02d}:45" in result.scheduled_start_datetime_str

    @pytest.mark.parametrize(
        "hour,expected_section",
        [
            (7, TaskChuteSection.A_07_10),
            (9, TaskChuteSection.A_07_10),
            (10, TaskChuteSection.B_10_13),
            (12, TaskChuteSection.B_10_13),
            (13, TaskChuteSection.C_13_17),
            (16, TaskChuteSection.C_13_17),
            (17, TaskChuteSection.D_17_19),
            (18, TaskChuteSection.D_17_19),
            (19, TaskChuteSection.E_19_22),
            (21, TaskChuteSection.E_19_22),
            (22, TaskChuteSection.F_22_24),
            (23, TaskChuteSection.F_22_24),
            (0, TaskChuteSection.G_24_07),
            (6, TaskChuteSection.G_24_07),
        ],
    )
    def test_execute_all_sections(self, hour: int, expected_section: TaskChuteSection) -> None:
        """すべてのセクションへの変換が正しく行われることをテスト"""
        # Arrange
        page_id = "test-page-id"
        # JSTオフセットを引いた時刻で設定 (naive datetimeはUTCとみなす)
        utc_hour = (hour - 9) % 24
        scheduled_datetime = datetime(2024, 3, 20, utc_hour, 0)
        mock_todo = ToDo(
            id=page_id,
            title="テストタスク",
            status=ToDoStatusEnum.TODO,
            section=None,
            scheduled_start_datetime=scheduled_datetime,
        )
        self.mock_repository.find.return_value = mock_todo

        # Act
        result = self.use_case.execute(page_id)

        # Assert
        assert result.new_section == expected_section


class TestOverrideSectionByScheduleExecuteAll:
    """execute_allメソッドのテスト"""

    def setup_method(self) -> None:
        self.mock_repository = Mock(spec=TodoRepository)
        self.use_case = OverrideSectionBySchedule(self.mock_repository)

    def test_execute_all_with_scheduled_todos(self) -> None:
        """予定開始日時が設定されたTODOがある場合の一括実行テスト"""
        # Arrange
        todo1 = ToDo(
            id="page-1",
            title="タスク1",
            status=ToDoStatusEnum.TODO,
            section=TaskChuteSection.A_07_10,
            scheduled_start_datetime=datetime(2024, 3, 19, 23, 30),  # JST 8:30
        )
        todo2 = ToDo(
            id="page-2",
            title="タスク2",
            status=ToDoStatusEnum.TODO,
            section=None,
            scheduled_start_datetime=datetime(2024, 3, 20, 5, 0),  # JST 14:00
        )
        self.mock_repository.find_by_status.return_value = [todo1, todo2]
        self.mock_repository.find.side_effect = [todo1, todo2]

        # Act
        result = self.use_case.execute_all()

        # Assert
        assert isinstance(result, OverrideSectionBulkResult)
        assert result.success_count == 2
        assert result.skipped_count == 0
        assert len(result.results) == 2
        self.mock_repository.find_by_status.assert_called_once_with(ToDoStatusEnum.TODO)

    def test_execute_all_with_mixed_todos(self) -> None:
        """予定開始日時があるものとないものが混在する場合のテスト"""
        # Arrange
        todo_with_schedule = ToDo(
            id="page-1",
            title="タスク1（予定あり）",
            status=ToDoStatusEnum.TODO,
            section=None,
            scheduled_start_datetime=datetime(2024, 3, 19, 23, 30),  # JST 8:30
        )
        todo_without_schedule = ToDo(
            id="page-2",
            title="タスク2（予定なし）",
            status=ToDoStatusEnum.TODO,
            section=None,
            scheduled_start_datetime=None,
        )
        self.mock_repository.find_by_status.return_value = [todo_with_schedule, todo_without_schedule]
        self.mock_repository.find.return_value = todo_with_schedule

        # Act
        result = self.use_case.execute_all()

        # Assert
        assert result.success_count == 1
        assert result.skipped_count == 1

    def test_execute_all_with_no_scheduled_todos(self) -> None:
        """予定開始日時が設定されたTODOがない場合のテスト"""
        # Arrange
        todo1 = ToDo(
            id="page-1",
            title="タスク1",
            status=ToDoStatusEnum.TODO,
            section=None,
            scheduled_start_datetime=None,
        )
        todo2 = ToDo(
            id="page-2",
            title="タスク2",
            status=ToDoStatusEnum.TODO,
            section=None,
            scheduled_start_datetime=None,
        )
        self.mock_repository.find_by_status.return_value = [todo1, todo2]

        # Act
        result = self.use_case.execute_all()

        # Assert
        assert result.success_count == 0
        assert result.skipped_count == 2

    def test_execute_all_with_empty_list(self) -> None:
        """TODOステータスのタスクが存在しない場合のテスト"""
        # Arrange
        self.mock_repository.find_by_status.return_value = []

        # Act
        result = self.use_case.execute_all()

        # Assert
        assert result.success_count == 0
        assert result.skipped_count == 0
        assert result.results == []

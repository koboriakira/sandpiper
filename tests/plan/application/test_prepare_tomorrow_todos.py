"""PrepareTomorrowTodos ユースケースのテスト"""

from datetime import date
from unittest.mock import MagicMock

import pytest

from sandpiper.perform.application.mark_remaining_todos_as_today import (
    MarkRemainingTodosAsToday,
    MarkRemainingTodosAsTodayResult,
)
from sandpiper.plan.application.create_repeat_project_task import CreateRepeatProjectTask
from sandpiper.plan.application.create_repeat_task import CreateRepeatTask
from sandpiper.plan.application.create_schedule_tasks import CreateScheduleTasks, CreateScheduleTasksResult
from sandpiper.plan.application.create_tasks_by_someday_list import (
    CreateTasksBySomedayList,
    CreateTasksBySomedayListResult,
)
from sandpiper.plan.application.prepare_tomorrow_todos import PrepareTomorrowTodos
from sandpiper.shared.infrastructure.archive_deleted_pages import ArchiveDeletedPages


class TestPrepareTomorrowTodos:
    @pytest.fixture()
    def mocks(self) -> dict[str, MagicMock]:
        mark_remaining_todos_as_today = MagicMock(spec=MarkRemainingTodosAsToday)
        create_repeat_project_task = MagicMock(spec=CreateRepeatProjectTask)
        create_repeat_task = MagicMock(spec=CreateRepeatTask)
        create_tasks_by_someday_list = MagicMock(spec=CreateTasksBySomedayList)
        create_schedule_tasks = MagicMock(spec=CreateScheduleTasks)
        archive_deleted_pages = MagicMock(spec=ArchiveDeletedPages)

        mark_remaining_todos_as_today.execute.return_value = MarkRemainingTodosAsTodayResult(marked_count=0)
        create_tasks_by_someday_list.execute.return_value = CreateTasksBySomedayListResult(
            created_count=0, created_titles=[]
        )
        create_schedule_tasks.execute.return_value = CreateScheduleTasksResult(created_count=0)

        return {
            "mark_remaining_todos_as_today": mark_remaining_todos_as_today,
            "create_repeat_project_task": create_repeat_project_task,
            "create_repeat_task": create_repeat_task,
            "create_tasks_by_someday_list": create_tasks_by_someday_list,
            "create_schedule_tasks": create_schedule_tasks,
            "archive_deleted_pages": archive_deleted_pages,
        }

    @pytest.fixture()
    def use_case(self, mocks: dict[str, MagicMock]) -> PrepareTomorrowTodos:
        return PrepareTomorrowTodos(**mocks)

    def test_execute_calls_all_steps_in_order(
        self, use_case: PrepareTomorrowTodos, mocks: dict[str, MagicMock]
    ) -> None:
        """全ステップが順番に呼ばれる"""
        basis_date = date(2026, 2, 26)

        result = use_case.execute(is_tomorrow=True, basis_date=basis_date)

        mocks["mark_remaining_todos_as_today"].execute.assert_called_once()
        mocks["archive_deleted_pages"].execute.assert_called_once()
        mocks["create_repeat_project_task"].execute.assert_called_once_with(is_tomorrow=True)
        mocks["create_repeat_task"].execute.assert_called_once_with(basis_date=basis_date)
        mocks["create_tasks_by_someday_list"].execute.assert_called_once_with(basis_date=basis_date)
        mocks["create_schedule_tasks"].execute.assert_called_once_with(target_date=basis_date)
        assert result.target_label == "明日"
        assert result.basis_date == basis_date

    def test_execute_today(self, use_case: PrepareTomorrowTodos, mocks: dict[str, MagicMock]) -> None:
        """is_tomorrow=Falseの場合「今日」ラベルになる"""
        basis_date = date(2026, 2, 25)

        result = use_case.execute(is_tomorrow=False, basis_date=basis_date)

        mocks["create_repeat_project_task"].execute.assert_called_once_with(is_tomorrow=False)
        assert result.target_label == "今日"

    def test_marked_as_today_count_in_result(self, use_case: PrepareTomorrowTodos, mocks: dict[str, MagicMock]) -> None:
        """フラグ設定件数が結果に含まれる"""
        mocks["mark_remaining_todos_as_today"].execute.return_value = MarkRemainingTodosAsTodayResult(marked_count=5)

        result = use_case.execute(is_tomorrow=True, basis_date=date(2026, 2, 26))

        assert result.marked_as_today_count == 5
        assert "今日やるフラグ5件" in result.summary

    def test_summary_with_counts(self, use_case: PrepareTomorrowTodos, mocks: dict[str, MagicMock]) -> None:
        """件数がサマリーに含まれる"""
        mocks["create_tasks_by_someday_list"].execute.return_value = CreateTasksBySomedayListResult(
            created_count=2, created_titles=["a", "b"]
        )
        mocks["create_schedule_tasks"].execute.return_value = CreateScheduleTasksResult(created_count=3)

        result = use_case.execute(is_tomorrow=True, basis_date=date(2026, 2, 26))

        assert "サムデイリストから2件" in result.summary
        assert "スケジュールから3件" in result.summary

    def test_summary_without_counts(self, use_case: PrepareTomorrowTodos) -> None:
        """件数がゼロの場合はシンプルなサマリー"""
        result = use_case.execute(is_tomorrow=True, basis_date=date(2026, 2, 26))

        assert result.summary == "明日のTODOリストを作成しました"


class TestResolveParamsFromNow:
    @pytest.mark.parametrize(
        ("hour", "expected_is_tomorrow", "expected_offset"),
        [
            (18, True, 1),
            (23, True, 1),
            (0, False, 0),
            (17, False, 0),
            (12, False, 0),
        ],
    )
    def test_resolve_params(self, hour: int, expected_is_tomorrow: bool, expected_offset: int) -> None:
        today = date(2026, 2, 25)
        is_tomorrow, basis_date = PrepareTomorrowTodos.resolve_params_from_now(now_hour=hour, today=today)

        assert is_tomorrow == expected_is_tomorrow
        assert basis_date == date(2026, 2, 25 + expected_offset)

"""繰り返しプロジェクトタスク作成ユースケースのテスト"""

from datetime import date
from unittest.mock import Mock, patch

import pytest

from sandpiper.plan.application.create_repeat_project_task import CreateRepeatProjectTask
from sandpiper.plan.query.project_task_dto import ProjectTaskDto
from sandpiper.shared.valueobject.todo_status_enum import ToDoStatusEnum


class TestCreateRepeatProjectTaskIsWeekend:
    """_is_weekendメソッドのテスト"""

    @pytest.mark.parametrize(
        "test_date,expected",
        [
            (date(2026, 1, 26), False),  # 月曜日
            (date(2026, 1, 27), False),  # 火曜日
            (date(2026, 1, 28), False),  # 水曜日
            (date(2026, 1, 29), False),  # 木曜日
            (date(2026, 1, 30), False),  # 金曜日
            (date(2026, 1, 31), True),  # 土曜日
            (date(2026, 2, 1), True),  # 日曜日
        ],
    )
    def test_is_weekend(self, test_date: date, expected: bool):
        """曜日判定が正しく動作することをテスト"""
        result = CreateRepeatProjectTask._is_weekend(test_date)
        assert result == expected


class TestCreateRepeatProjectTaskExcludeWorkProjectTasks:
    """_exclude_work_project_tasksメソッドのテスト"""

    def _create_dto(self, page_id: str, is_work_project: bool) -> ProjectTaskDto:
        return ProjectTaskDto(
            page_id=page_id,
            title=f"タスク-{page_id}",
            status=ToDoStatusEnum.TODO,
            project_page_id=f"project-{page_id}",
            is_next=True,
            is_work_project=is_work_project,
        )

    def test_exclude_work_project_tasks_removes_work_projects(self):
        """仕事系プロジェクトのタスクが除外されることをテスト"""
        # Arrange
        tasks = [
            self._create_dto("1", is_work_project=True),
            self._create_dto("2", is_work_project=False),
            self._create_dto("3", is_work_project=True),
            self._create_dto("4", is_work_project=False),
        ]

        # Act
        result = CreateRepeatProjectTask._exclude_work_project_tasks(tasks)

        # Assert
        assert len(result) == 2
        assert result[0].page_id == "2"
        assert result[1].page_id == "4"

    def test_exclude_work_project_tasks_all_work_projects(self):
        """全て仕事系プロジェクトの場合、空リストが返されることをテスト"""
        # Arrange
        tasks = [
            self._create_dto("1", is_work_project=True),
            self._create_dto("2", is_work_project=True),
        ]

        # Act
        result = CreateRepeatProjectTask._exclude_work_project_tasks(tasks)

        # Assert
        assert len(result) == 0

    def test_exclude_work_project_tasks_no_work_projects(self):
        """仕事系プロジェクトがない場合、全タスクが返されることをテスト"""
        # Arrange
        tasks = [
            self._create_dto("1", is_work_project=False),
            self._create_dto("2", is_work_project=False),
        ]

        # Act
        result = CreateRepeatProjectTask._exclude_work_project_tasks(tasks)

        # Assert
        assert len(result) == 2

    def test_exclude_work_project_tasks_empty_list(self):
        """空リストの場合、空リストが返されることをテスト"""
        # Act
        result = CreateRepeatProjectTask._exclude_work_project_tasks([])

        # Assert
        assert result == []


class TestCreateRepeatProjectTaskExecute:
    """executeメソッドのテスト"""

    def setup_method(self):
        """各テストメソッドの前に実行されるセットアップ"""
        self.mock_query = Mock()
        self.mock_repository = Mock()
        self.use_case = CreateRepeatProjectTask(
            project_task_query=self.mock_query,
            todo_repository=self.mock_repository,
        )

    def _create_dto(self, page_id: str, project_id: str, is_work_project: bool) -> ProjectTaskDto:
        return ProjectTaskDto(
            page_id=page_id,
            title=f"タスク-{page_id}",
            status=ToDoStatusEnum.TODO,
            project_page_id=project_id,
            is_next=True,
            is_work_project=is_work_project,
        )

    @patch("sandpiper.plan.application.create_repeat_project_task.jst_today")
    def test_execute_weekday_includes_all_tasks(self, mock_jst_today):
        """平日の場合、仕事系プロジェクトのタスクも含まれることをテスト"""
        # Arrange - 月曜日
        mock_jst_today.return_value = date(2026, 1, 26)
        tasks = [
            self._create_dto("1", "proj-a", is_work_project=True),
            self._create_dto("2", "proj-b", is_work_project=False),
        ]
        self.mock_query.fetch_undone_project_tasks.return_value = tasks

        # Act
        self.use_case.execute(is_tomorrow=False)

        # Assert - 2回saveが呼ばれる(両方のタスク)
        assert self.mock_repository.save.call_count == 2

    @patch("sandpiper.plan.application.create_repeat_project_task.jst_today")
    def test_execute_saturday_excludes_work_projects(self, mock_jst_today):
        """土曜日の場合、仕事系プロジェクトのタスクが除外されることをテスト"""
        # Arrange - 土曜日
        mock_jst_today.return_value = date(2026, 1, 31)
        tasks = [
            self._create_dto("1", "proj-a", is_work_project=True),
            self._create_dto("2", "proj-b", is_work_project=False),
        ]
        self.mock_query.fetch_undone_project_tasks.return_value = tasks

        # Act
        self.use_case.execute(is_tomorrow=False)

        # Assert - 1回だけsaveが呼ばれる(非仕事系タスクのみ)
        assert self.mock_repository.save.call_count == 1
        saved_call = self.mock_repository.save.call_args
        saved_todo = saved_call[0][0]
        assert saved_todo.project_page_id == "proj-b"

    @patch("sandpiper.plan.application.create_repeat_project_task.jst_today")
    def test_execute_sunday_excludes_work_projects(self, mock_jst_today):
        """日曜日の場合、仕事系プロジェクトのタスクが除外されることをテスト"""
        # Arrange - 日曜日
        mock_jst_today.return_value = date(2026, 2, 1)
        tasks = [
            self._create_dto("1", "proj-a", is_work_project=True),
            self._create_dto("2", "proj-b", is_work_project=False),
        ]
        self.mock_query.fetch_undone_project_tasks.return_value = tasks

        # Act
        self.use_case.execute(is_tomorrow=False)

        # Assert - 1回だけsaveが呼ばれる(非仕事系タスクのみ)
        assert self.mock_repository.save.call_count == 1

    @patch("sandpiper.plan.application.create_repeat_project_task.jst_today")
    def test_execute_tomorrow_saturday_excludes_work_projects(self, mock_jst_today):
        """金曜日にis_tomorrow=Trueで実行した場合、土曜日として判定されることをテスト"""
        # Arrange - 金曜日(明日は土曜日)
        mock_jst_today.return_value = date(2026, 1, 30)
        tasks = [
            self._create_dto("1", "proj-a", is_work_project=True),
            self._create_dto("2", "proj-b", is_work_project=False),
        ]
        self.mock_query.fetch_undone_project_tasks.return_value = tasks

        # Act
        self.use_case.execute(is_tomorrow=True)

        # Assert - 明日(土曜日)なので仕事系は除外、1回だけsave
        assert self.mock_repository.save.call_count == 1
        saved_call = self.mock_repository.save.call_args
        saved_todo = saved_call[0][0]
        assert saved_todo.project_page_id == "proj-b"

    @patch("sandpiper.plan.application.create_repeat_project_task.jst_today")
    def test_execute_tomorrow_monday_includes_all_tasks(self, mock_jst_today):
        """日曜日にis_tomorrow=Trueで実行した場合、月曜日として判定されることをテスト"""
        # Arrange - 日曜日(明日は月曜日)
        mock_jst_today.return_value = date(2026, 2, 1)
        tasks = [
            self._create_dto("1", "proj-a", is_work_project=True),
            self._create_dto("2", "proj-b", is_work_project=False),
        ]
        self.mock_query.fetch_undone_project_tasks.return_value = tasks

        # Act
        self.use_case.execute(is_tomorrow=True)

        # Assert - 明日(月曜日)なので全タスク含まれる
        assert self.mock_repository.save.call_count == 2

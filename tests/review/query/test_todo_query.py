from datetime import date, datetime
from unittest.mock import Mock

import pytest
from lotion import BasePage, Lotion

from sandpiper.review.query.activity_log_item import ActivityType
from sandpiper.review.query.todo_query import NotionTodoQuery


class TestNotionTodoQuery:
    @pytest.fixture
    def mock_lotion_client(self, monkeypatch):
        mock_client = Mock(spec=Lotion)
        monkeypatch.setattr(Lotion, "get_instance", lambda: mock_client)
        return mock_client

    @pytest.fixture
    def query(self, mock_lotion_client):  # noqa: ARG002
        return NotionTodoQuery()

    @pytest.fixture
    def target_date(self):
        return date(2024, 1, 15)

    def test_fetch_done_todos_by_date_empty_result(self, query, mock_lotion_client, target_date):
        # Arrange
        mock_lotion_client.retrieve_database.return_value = []

        # Act
        result = query.fetch_done_todos_by_date(target_date)

        # Assert
        assert result == []
        assert mock_lotion_client.retrieve_database.call_count == 2

    def test_fetch_done_todos_by_date_filters_non_done_status(self, query, mock_lotion_client, target_date):
        # Arrange
        mock_todo = self._create_mock_todo_item()
        mock_status = Mock()
        mock_status.status_name = "ToDo"  # Not DONE
        mock_todo.get_status.return_value = mock_status

        mock_lotion_client.retrieve_database.side_effect = [
            [mock_todo],  # TODO database
            [],  # PROJECT database
        ]

        # Act
        result = query.fetch_done_todos_by_date(target_date)

        # Assert
        assert result == []

    def test_fetch_done_todos_by_date_filters_missing_perform_range(self, query, mock_lotion_client, target_date):
        # Arrange
        mock_todo = self._create_mock_todo_item()
        self._setup_done_status(mock_todo)

        # perform_range が None の場合
        mock_date_range = Mock()
        mock_date_range.start = None
        mock_date_range.end = None
        mock_todo.get_date.return_value = mock_date_range

        mock_lotion_client.retrieve_database.side_effect = [[mock_todo], []]

        # Act
        result = query.fetch_done_todos_by_date(target_date)

        # Assert
        assert result == []

    def test_fetch_done_todos_by_date_filters_before_target_date(self, query, mock_lotion_client, target_date):
        # Arrange
        mock_todo = self._create_mock_todo_item()
        self._setup_done_status(mock_todo)
        # 指定日付より前の日付
        self._setup_perform_range(mock_todo, "2024-01-14T09:00:00", "2024-01-14T10:00:00")
        self._setup_valid_task_kind(mock_todo, "単発")

        mock_lotion_client.retrieve_database.side_effect = [[mock_todo], []]

        # Act
        result = query.fetch_done_todos_by_date(target_date)

        # Assert
        assert result == []

    def test_fetch_done_todos_by_date_filters_missing_task_kind(self, query, mock_lotion_client, target_date):
        # Arrange
        mock_todo = self._create_mock_todo_item()
        self._setup_done_status(mock_todo)
        self._setup_valid_perform_range(mock_todo)

        # タスク種別が空の場合
        mock_select = Mock()
        mock_select.selected_name = None
        mock_todo.get_select.return_value = mock_select

        mock_lotion_client.retrieve_database.side_effect = [[mock_todo], []]

        # Act
        result = query.fetch_done_todos_by_date(target_date)

        # Assert
        assert result == []

    def test_fetch_done_todos_by_date_single_todo_success(self, query, mock_lotion_client, target_date):
        # Arrange
        mock_todo = self._create_mock_todo_item()
        self._setup_done_status(mock_todo)
        self._setup_valid_perform_range(mock_todo)
        self._setup_valid_task_kind(mock_todo, "単発")
        mock_todo.get_title_text.return_value = "テストタスク"
        mock_todo.id = "test-todo-id"

        mock_lotion_client.retrieve_database.side_effect = [[mock_todo], []]

        # Act
        result = query.fetch_done_todos_by_date(target_date)

        # Assert
        assert len(result) == 1
        activity = result[0]
        assert activity.activity_type == ActivityType.TODO
        assert activity.title == "テストタスク"
        assert activity.kind == "単発"
        assert activity.project_name == ""
        assert isinstance(activity.start_datetime, datetime)
        assert isinstance(activity.end_datetime, datetime)

    def test_fetch_done_todos_by_date_project_task_success(self, query, mock_lotion_client, target_date):
        # Arrange
        mock_todo = self._create_mock_todo_item()
        self._setup_done_status(mock_todo)
        self._setup_valid_perform_range(mock_todo)
        self._setup_valid_task_kind(mock_todo, "プロジェクト")
        mock_todo.get_title_text.return_value = "プロジェクトタスク"
        mock_todo.id = "project-todo-id"

        # プロジェクト関連の設定
        mock_relation = Mock()
        mock_relation.id_list = ["project-123"]
        mock_todo.get_relation.return_value = mock_relation

        # プロジェクトページのモック
        mock_project = Mock(spec=BasePage)
        mock_project.id = "project-123"
        mock_project.get_title_text.return_value = "テストプロジェクト"

        mock_lotion_client.retrieve_database.side_effect = [[mock_todo], [mock_project]]

        # Act
        result = query.fetch_done_todos_by_date(target_date)

        # Assert
        assert len(result) == 1
        activity = result[0]
        assert activity.activity_type == ActivityType.TODO
        assert activity.title == "プロジェクトタスク"
        assert activity.kind == "プロジェクト"
        assert activity.project_name == "テストプロジェクト"

    def test_fetch_done_todos_by_date_project_task_no_relation(self, query, mock_lotion_client, target_date):
        # Arrange
        mock_todo = self._create_mock_todo_item()
        self._setup_done_status(mock_todo)
        self._setup_valid_perform_range(mock_todo)
        self._setup_valid_task_kind(mock_todo, "プロジェクト")

        # プロジェクト関連が空の場合
        mock_relation = Mock()
        mock_relation.id_list = []
        mock_todo.get_relation.return_value = mock_relation

        mock_lotion_client.retrieve_database.side_effect = [[mock_todo], []]

        # Act
        result = query.fetch_done_todos_by_date(target_date)

        # Assert
        assert result == []

    def test_fetch_done_todos_by_date_multiple_todos(self, query, mock_lotion_client, target_date):
        # Arrange
        mock_todo1 = self._create_mock_todo_item()
        self._setup_done_status(mock_todo1)
        self._setup_valid_perform_range(mock_todo1)
        self._setup_valid_task_kind(mock_todo1, "単発")
        mock_todo1.get_title_text.return_value = "タスク1"
        mock_todo1.id = "todo-1"

        mock_todo2 = self._create_mock_todo_item()
        self._setup_done_status(mock_todo2)
        self._setup_valid_perform_range(mock_todo2)
        self._setup_valid_task_kind(mock_todo2, "差し込み")
        mock_todo2.get_title_text.return_value = "タスク2"
        mock_todo2.id = "todo-2"

        mock_lotion_client.retrieve_database.side_effect = [[mock_todo1, mock_todo2], []]

        # Act
        result = query.fetch_done_todos_by_date(target_date)

        # Assert
        assert len(result) == 2
        assert result[0].title == "タスク1"
        assert result[0].kind == "単発"
        assert result[1].title == "タスク2"
        assert result[1].kind == "差し込み"

    def _create_mock_todo_item(self):
        """モックのToDo項目を作成"""
        mock_item = Mock()
        mock_item.id = "mock-id"
        return mock_item

    def _setup_done_status(self, mock_todo):
        """Done ステータスを設定"""
        mock_status = Mock()
        mock_status.status_name = "Done"
        mock_todo.get_status.return_value = mock_status

    def _setup_valid_perform_range(self, mock_todo):
        """有効な実施期間を設定(target_date以降)"""
        self._setup_perform_range(mock_todo, "2024-01-15T09:00:00", "2024-01-15T10:00:00")

    def _setup_perform_range(self, mock_todo, start: str, end: str):
        """実施期間を設定"""
        mock_date_range = Mock()
        mock_date_range.start = start
        mock_date_range.end = end
        mock_todo.get_date.return_value = mock_date_range

    def _setup_valid_task_kind(self, mock_todo, kind_name: str):
        """有効なタスク種別を設定"""
        mock_select = Mock()
        mock_select.selected_name = kind_name
        mock_todo.get_select.return_value = mock_select

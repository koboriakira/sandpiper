from unittest.mock import Mock, call

from sandpiper.plan.application.create_tasks_by_someday_list import (
    CreateTasksBySomedayList,
    CreateTasksBySomedayListResult,
)
from sandpiper.plan.domain.someday_item import SomedayItem, SomedayTiming
from sandpiper.plan.domain.someday_repository import SomedayRepository
from sandpiper.plan.domain.todo import ToDo, ToDoKind
from sandpiper.plan.domain.todo_repository import TodoRepository


class TestCreateTasksBySomedayList:
    def setup_method(self):
        self.mock_someday_repository = Mock(spec=SomedayRepository)
        self.mock_todo_repository = Mock(spec=TodoRepository)
        self.service = CreateTasksBySomedayList(
            someday_repository=self.mock_someday_repository,
            todo_repository=self.mock_todo_repository,
        )

    def test_execute_with_no_items(self):
        """明日やるアイテムがない場合のテスト"""
        # Arrange
        self.mock_someday_repository.fetch_tomorrow_items.return_value = []

        # Act
        result = self.service.execute()

        # Assert
        assert result.created_count == 0
        assert result.created_titles == []
        self.mock_todo_repository.save.assert_not_called()
        self.mock_someday_repository.delete.assert_not_called()

    def test_execute_with_single_item(self):
        """1つのアイテムがある場合のテスト"""
        # Arrange
        someday_item = SomedayItem(
            id="someday-1",
            title="明日やるタスク",
            timing=SomedayTiming.TOMORROW,
            do_tomorrow=True,
        )
        self.mock_someday_repository.fetch_tomorrow_items.return_value = [someday_item]

        # Act
        result = self.service.execute()

        # Assert
        assert result.created_count == 1
        assert result.created_titles == ["明日やるタスク"]

        # TODOが作成されたことを確認
        self.mock_todo_repository.save.assert_called_once()
        saved_todo = self.mock_todo_repository.save.call_args[0][0]
        assert isinstance(saved_todo, ToDo)
        assert saved_todo.title == "明日やるタスク"
        assert saved_todo.kind == ToDoKind.SINGLE

        # サムデイアイテムが削除されたことを確認
        self.mock_someday_repository.delete.assert_called_once_with("someday-1")

    def test_execute_with_multiple_items(self):
        """複数のアイテムがある場合のテスト"""
        # Arrange
        items = [
            SomedayItem(
                id="someday-1",
                title="タスク1",
                timing=SomedayTiming.TOMORROW,
                do_tomorrow=True,
            ),
            SomedayItem(
                id="someday-2",
                title="タスク2",
                timing=SomedayTiming.SOMEDAY,
                do_tomorrow=True,
            ),
            SomedayItem(
                id="someday-3",
                title="タスク3",
                timing=SomedayTiming.TOMORROW,
                do_tomorrow=True,
            ),
        ]
        self.mock_someday_repository.fetch_tomorrow_items.return_value = items

        # Act
        result = self.service.execute()

        # Assert
        assert result.created_count == 3
        assert result.created_titles == ["タスク1", "タスク2", "タスク3"]

        # TODOが3回作成されたことを確認
        assert self.mock_todo_repository.save.call_count == 3

        # 全てのTODOがSINGLE種別であることを確認
        for call_args in self.mock_todo_repository.save.call_args_list:
            saved_todo = call_args[0][0]
            assert saved_todo.kind == ToDoKind.SINGLE

        # サムデイアイテムが3回削除されたことを確認
        assert self.mock_someday_repository.delete.call_count == 3
        self.mock_someday_repository.delete.assert_has_calls([call("someday-1"), call("someday-2"), call("someday-3")])

    def test_todo_created_with_correct_kind(self):
        """TODOが正しいタスク種別で作成されることを確認"""
        # Arrange
        someday_item = SomedayItem(
            id="someday-1",
            title="単発タスク",
            timing=SomedayTiming.TOMORROW,
            do_tomorrow=True,
        )
        self.mock_someday_repository.fetch_tomorrow_items.return_value = [someday_item]

        # Act
        self.service.execute()

        # Assert
        saved_todo = self.mock_todo_repository.save.call_args[0][0]
        assert saved_todo.kind == ToDoKind.SINGLE


class TestCreateTasksBySomedayListResult:
    def test_result_creation(self):
        """結果オブジェクトの作成をテスト"""
        # Act
        result = CreateTasksBySomedayListResult(
            created_count=3,
            created_titles=["タスク1", "タスク2", "タスク3"],
        )

        # Assert
        assert result.created_count == 3
        assert result.created_titles == ["タスク1", "タスク2", "タスク3"]

    def test_result_with_empty_list(self):
        """空のリストでの結果オブジェクトをテスト"""
        # Act
        result = CreateTasksBySomedayListResult(
            created_count=0,
            created_titles=[],
        )

        # Assert
        assert result.created_count == 0
        assert result.created_titles == []

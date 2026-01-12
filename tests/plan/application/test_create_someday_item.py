from unittest.mock import Mock

from sandpiper.plan.application.create_someday_item import (
    CreateSomedayItem,
    CreateSomedayItemRequest,
    CreateSomedayItemResult,
)
from sandpiper.plan.domain.someday_item import SomedayItem, SomedayTiming
from sandpiper.plan.domain.someday_repository import SomedayRepository


class TestCreateSomedayItem:
    def setup_method(self):
        self.mock_someday_repository = Mock(spec=SomedayRepository)
        self.service = CreateSomedayItem(
            someday_repository=self.mock_someday_repository,
        )

    def test_execute_creates_item_with_tomorrow_timing(self):
        """アイテムがタイミング「明日」で作成されることを確認"""
        # Arrange
        saved_item = SomedayItem(
            id="created-item-1",
            title="テストアイテム",
            timing=SomedayTiming.TOMORROW,
            do_tomorrow=False,
            is_deleted=False,
        )
        self.mock_someday_repository.save.return_value = saved_item

        request = CreateSomedayItemRequest(title="テストアイテム")

        # Act
        result = self.service.execute(request)

        # Assert
        assert result.id == "created-item-1"
        assert result.title == "テストアイテム"
        assert result.timing == "明日"

        # saveが呼ばれたことを確認
        self.mock_someday_repository.save.assert_called_once()
        saved_arg = self.mock_someday_repository.save.call_args[0][0]
        assert isinstance(saved_arg, SomedayItem)
        assert saved_arg.title == "テストアイテム"
        assert saved_arg.timing == SomedayTiming.TOMORROW

    def test_execute_always_uses_tomorrow_timing(self):
        """タイミングが常に「明日」になることを確認"""
        # Arrange
        saved_item = SomedayItem(
            id="item-2",
            title="別のアイテム",
            timing=SomedayTiming.TOMORROW,
        )
        self.mock_someday_repository.save.return_value = saved_item

        request = CreateSomedayItemRequest(title="別のアイテム")

        # Act
        self.service.execute(request)

        # Assert
        saved_arg = self.mock_someday_repository.save.call_args[0][0]
        assert saved_arg.timing == SomedayTiming.TOMORROW

    def test_execute_returns_correct_result(self):
        """正しい結果オブジェクトが返されることを確認"""
        # Arrange
        saved_item = SomedayItem(
            id="result-item",
            title="結果確認用アイテム",
            timing=SomedayTiming.TOMORROW,
        )
        self.mock_someday_repository.save.return_value = saved_item

        request = CreateSomedayItemRequest(title="結果確認用アイテム")

        # Act
        result = self.service.execute(request)

        # Assert
        assert isinstance(result, CreateSomedayItemResult)
        assert result.id == "result-item"
        assert result.title == "結果確認用アイテム"
        assert result.timing == "明日"


class TestCreateSomedayItemRequest:
    def test_request_creation(self):
        """リクエストオブジェクトの作成をテスト"""
        # Act
        request = CreateSomedayItemRequest(title="テストタイトル")

        # Assert
        assert request.title == "テストタイトル"


class TestCreateSomedayItemResult:
    def test_result_creation(self):
        """結果オブジェクトの作成をテスト"""
        # Act
        result = CreateSomedayItemResult(
            id="test-id",
            title="テストタイトル",
            timing="明日",
        )

        # Assert
        assert result.id == "test-id"
        assert result.title == "テストタイトル"
        assert result.timing == "明日"

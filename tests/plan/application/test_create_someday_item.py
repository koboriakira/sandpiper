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

    def test_execute_creates_item_with_default_tomorrow_timing(self):
        """デフォルトでタイミング「明日」で作成されることを確認"""
        # Arrange
        saved_item = SomedayItem(
            id="created-item-1",
            title="テストアイテム",
            timing=SomedayTiming.TOMORROW,
            do_tomorrow=False,
            is_deleted=False,
            context=[],
        )
        self.mock_someday_repository.save.return_value = saved_item

        request = CreateSomedayItemRequest(title="テストアイテム")

        # Act
        result = self.service.execute(request)

        # Assert
        assert result.id == "created-item-1"
        assert result.title == "テストアイテム"
        assert result.timing == "明日"
        assert result.do_tomorrow is False
        assert result.context == []

        # saveが呼ばれたことを確認
        self.mock_someday_repository.save.assert_called_once()
        saved_arg = self.mock_someday_repository.save.call_args[0][0]
        assert isinstance(saved_arg, SomedayItem)
        assert saved_arg.title == "テストアイテム"
        assert saved_arg.timing == SomedayTiming.TOMORROW

    def test_execute_with_custom_timing(self):
        """カスタムタイミングで作成できることを確認"""
        # Arrange
        saved_item = SomedayItem(
            id="item-2",
            title="いつかやるアイテム",
            timing=SomedayTiming.SOMEDAY,
            do_tomorrow=False,
            is_deleted=False,
            context=[],
        )
        self.mock_someday_repository.save.return_value = saved_item

        request = CreateSomedayItemRequest(
            title="いつかやるアイテム",
            timing=SomedayTiming.SOMEDAY,
        )

        # Act
        result = self.service.execute(request)

        # Assert
        assert result.timing == "いつか"
        saved_arg = self.mock_someday_repository.save.call_args[0][0]
        assert saved_arg.timing == SomedayTiming.SOMEDAY

    def test_execute_with_do_tomorrow_flag(self):
        """明日やるフラグを設定できることを確認"""
        # Arrange
        saved_item = SomedayItem(
            id="item-3",
            title="明日やるアイテム",
            timing=SomedayTiming.TOMORROW,
            do_tomorrow=True,
            is_deleted=False,
            context=[],
        )
        self.mock_someday_repository.save.return_value = saved_item

        request = CreateSomedayItemRequest(
            title="明日やるアイテム",
            do_tomorrow=True,
        )

        # Act
        result = self.service.execute(request)

        # Assert
        assert result.do_tomorrow is True
        saved_arg = self.mock_someday_repository.save.call_args[0][0]
        assert saved_arg.do_tomorrow is True

    def test_execute_with_context(self):
        """コンテクストを設定できることを確認"""
        # Arrange
        saved_item = SomedayItem(
            id="item-4",
            title="コンテクスト付きアイテム",
            timing=SomedayTiming.TOMORROW,
            do_tomorrow=False,
            is_deleted=False,
            context=["外出", "仕事"],
        )
        self.mock_someday_repository.save.return_value = saved_item

        request = CreateSomedayItemRequest(
            title="コンテクスト付きアイテム",
            context=["外出", "仕事"],
        )

        # Act
        result = self.service.execute(request)

        # Assert
        assert result.context == ["外出", "仕事"]
        saved_arg = self.mock_someday_repository.save.call_args[0][0]
        assert saved_arg.context == ["外出", "仕事"]

    def test_execute_with_all_options(self):
        """すべてのオプションを指定できることを確認"""
        # Arrange
        saved_item = SomedayItem(
            id="item-5",
            title="全オプションアイテム",
            timing=SomedayTiming.INCIDENTALLY,
            do_tomorrow=True,
            is_deleted=False,
            context=["仕事"],
        )
        self.mock_someday_repository.save.return_value = saved_item

        request = CreateSomedayItemRequest(
            title="全オプションアイテム",
            timing=SomedayTiming.INCIDENTALLY,
            do_tomorrow=True,
            context=["仕事"],
        )

        # Act
        result = self.service.execute(request)

        # Assert
        assert result.id == "item-5"
        assert result.title == "全オプションアイテム"
        assert result.timing == "ついでに"
        assert result.do_tomorrow is True
        assert result.context == ["仕事"]

    def test_execute_returns_correct_result(self):
        """正しい結果オブジェクトが返されることを確認"""
        # Arrange
        saved_item = SomedayItem(
            id="result-item",
            title="結果確認用アイテム",
            timing=SomedayTiming.TOMORROW,
            do_tomorrow=False,
            is_deleted=False,
            context=[],
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
        assert result.do_tomorrow is False
        assert result.context == []


class TestCreateSomedayItemRequest:
    def test_request_creation_with_defaults(self):
        """デフォルト値でリクエストオブジェクトを作成できることをテスト"""
        # Act
        request = CreateSomedayItemRequest(title="テストタイトル")

        # Assert
        assert request.title == "テストタイトル"
        assert request.timing == SomedayTiming.TOMORROW
        assert request.do_tomorrow is False
        assert request.context == []

    def test_request_creation_with_all_options(self):
        """すべてのオプションでリクエストオブジェクトを作成できることをテスト"""
        # Act
        request = CreateSomedayItemRequest(
            title="テストタイトル",
            timing=SomedayTiming.SOMEDAY,
            do_tomorrow=True,
            context=["外出", "仕事"],
        )

        # Assert
        assert request.title == "テストタイトル"
        assert request.timing == SomedayTiming.SOMEDAY
        assert request.do_tomorrow is True
        assert request.context == ["外出", "仕事"]


class TestCreateSomedayItemResult:
    def test_result_creation(self):
        """結果オブジェクトの作成をテスト"""
        # Act
        result = CreateSomedayItemResult(
            id="test-id",
            title="テストタイトル",
            timing="明日",
            do_tomorrow=False,
            context=[],
        )

        # Assert
        assert result.id == "test-id"
        assert result.title == "テストタイトル"
        assert result.timing == "明日"
        assert result.do_tomorrow is False
        assert result.context == []

    def test_result_creation_with_all_fields(self):
        """すべてのフィールドで結果オブジェクトを作成できることをテスト"""
        # Act
        result = CreateSomedayItemResult(
            id="test-id",
            title="テストタイトル",
            timing="いつか",
            do_tomorrow=True,
            context=["外出"],
        )

        # Assert
        assert result.id == "test-id"
        assert result.title == "テストタイトル"
        assert result.timing == "いつか"
        assert result.do_tomorrow is True
        assert result.context == ["外出"]

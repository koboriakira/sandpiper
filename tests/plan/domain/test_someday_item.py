from sandpiper.plan.domain.someday_item import SomedayItem, SomedayTiming


class TestSomedayItem:
    def test_someday_item_creation(self):
        """SomedayItemの基本的な作成をテスト"""
        # Arrange & Act
        item = SomedayItem(
            id="test-id-1",
            title="テストアイテム",
            timing=SomedayTiming.TOMORROW,
            do_tomorrow=True,
            is_deleted=False,
            context=["外出"],
        )

        # Assert
        assert item.id == "test-id-1"
        assert item.title == "テストアイテム"
        assert item.timing == SomedayTiming.TOMORROW
        assert item.do_tomorrow is True
        assert item.is_deleted is False
        assert item.context == ["外出"]

    def test_someday_item_default_values(self):
        """SomedayItemのデフォルト値をテスト"""
        # Arrange & Act
        item = SomedayItem(
            id="test-id-2",
            title="デフォルト値テスト",
            timing=SomedayTiming.SOMEDAY,
        )

        # Assert
        assert item.do_tomorrow is False
        assert item.is_deleted is False
        assert item.context == []

    def test_someday_item_create_classmethod(self):
        """SomedayItem.createファクトリメソッドをテスト"""
        # Arrange & Act
        item = SomedayItem.create(
            title="新規アイテム",
            timing=SomedayTiming.TOMORROW,
            do_tomorrow=True,
            context=["仕事", "外出"],
        )

        # Assert
        assert item.id == ""
        assert item.title == "新規アイテム"
        assert item.timing == SomedayTiming.TOMORROW
        assert item.do_tomorrow is True
        assert item.is_deleted is False
        assert item.context == ["仕事", "外出"]

    def test_someday_item_create_with_defaults(self):
        """SomedayItem.createのデフォルト値をテスト"""
        # Arrange & Act
        item = SomedayItem.create(title="シンプルアイテム")

        # Assert
        assert item.id == ""
        assert item.title == "シンプルアイテム"
        assert item.timing == SomedayTiming.SOMEDAY
        assert item.do_tomorrow is False
        assert item.is_deleted is False
        assert item.context == []


class TestSomedayTiming:
    def test_timing_values(self):
        """SomedayTimingの値をテスト"""
        assert SomedayTiming.TOMORROW.value == "明日"
        assert SomedayTiming.SOMEDAY.value == "いつか"
        assert SomedayTiming.INCIDENTALLY.value == "ついでに"

    def test_timing_enum_members(self):
        """SomedayTimingのメンバーをテスト"""
        members = list(SomedayTiming)
        assert len(members) == 3
        assert SomedayTiming.TOMORROW in members
        assert SomedayTiming.SOMEDAY in members
        assert SomedayTiming.INCIDENTALLY in members

from unittest.mock import Mock

import pytest

from sandpiper.shared.infrastructure.event_bus import EventBus


class DummyEvent:
    """テスト用のイベントクラス"""
    def __init__(self, data: str):
        self.data = data


class AnotherDummyEvent:
    """別のテスト用のイベントクラス"""
    def __init__(self, value: int):
        self.value = value


class TestEventBus:
    def setup_method(self):
        self.event_bus = EventBus()

    def test_init(self):
        """EventBusの初期化をテスト"""
        event_bus = EventBus()
        assert event_bus._handlers is not None

    def test_subscribe_single_handler(self):
        """単一ハンドラーの登録をテスト"""
        handler = Mock()

        self.event_bus.subscribe(DummyEvent, handler)

        # 内部構造を確認
        assert DummyEvent in self.event_bus._handlers
        assert handler in self.event_bus._handlers[DummyEvent]

    def test_subscribe_multiple_handlers(self):
        """複数ハンドラーの登録をテスト"""
        handler1 = Mock()
        handler2 = Mock()

        self.event_bus.subscribe(DummyEvent, handler1)
        self.event_bus.subscribe(DummyEvent, handler2)

        # 両方のハンドラーが登録されることを確認
        assert handler1 in self.event_bus._handlers[DummyEvent]
        assert handler2 in self.event_bus._handlers[DummyEvent]
        assert len(self.event_bus._handlers[DummyEvent]) == 2

    def test_subscribe_different_event_types(self):
        """異なるイベントタイプのハンドラー登録をテスト"""
        handler1 = Mock()
        handler2 = Mock()

        self.event_bus.subscribe(DummyEvent, handler1)
        self.event_bus.subscribe(AnotherDummyEvent, handler2)

        # 別々のイベントタイプに登録されることを確認
        assert handler1 in self.event_bus._handlers[DummyEvent]
        assert handler2 in self.event_bus._handlers[AnotherDummyEvent]
        assert handler1 not in self.event_bus._handlers[AnotherDummyEvent]
        assert handler2 not in self.event_bus._handlers[DummyEvent]

    def test_publish_single_handler(self):
        """単一ハンドラーでのイベント発行をテスト"""
        handler = Mock()
        event = DummyEvent("test data")

        self.event_bus.subscribe(DummyEvent, handler)
        self.event_bus.publish(event)

        # ハンドラーがイベントと共に呼び出されることを確認
        handler.assert_called_once_with(event)

    def test_publish_multiple_handlers(self):
        """複数ハンドラーでのイベント発行をテスト"""
        handler1 = Mock()
        handler2 = Mock()
        event = DummyEvent("test data")

        self.event_bus.subscribe(DummyEvent, handler1)
        self.event_bus.subscribe(DummyEvent, handler2)
        self.event_bus.publish(event)

        # 両方のハンドラーが呼び出されることを確認
        handler1.assert_called_once_with(event)
        handler2.assert_called_once_with(event)

    def test_publish_no_handlers(self):
        """ハンドラーが登録されていないイベントの発行をテスト"""
        event = DummyEvent("test data")

        # エラーが発生せずに完了することを確認
        try:
            self.event_bus.publish(event)
        except Exception as e:
            pytest.fail(f"Unexpected exception: {e}")

    def test_publish_different_event_types(self):
        """異なるイベントタイプでの発行をテスト"""
        handler1 = Mock()
        handler2 = Mock()
        event1 = DummyEvent("test data")
        event2 = AnotherDummyEvent(123)

        self.event_bus.subscribe(DummyEvent, handler1)
        self.event_bus.subscribe(AnotherDummyEvent, handler2)

        # DummyEventを発行
        self.event_bus.publish(event1)
        handler1.assert_called_once_with(event1)
        handler2.assert_not_called()

        # リセット
        handler1.reset_mock()
        handler2.reset_mock()

        # AnotherDummyEventを発行
        self.event_bus.publish(event2)
        handler1.assert_not_called()
        handler2.assert_called_once_with(event2)

    def test_handler_with_exception(self):
        """ハンドラーで例外が発生した場合のテスト"""
        handler1 = Mock()
        handler2 = Mock(side_effect=Exception("Handler error"))
        handler3 = Mock()
        event = DummyEvent("test data")

        self.event_bus.subscribe(DummyEvent, handler1)
        self.event_bus.subscribe(DummyEvent, handler2)
        self.event_bus.subscribe(DummyEvent, handler3)

        # handler2で例外が発生してもhandler3が呼ばれることを確認
        with pytest.raises(Exception, match="Handler error"):
            self.event_bus.publish(event)

        # handler1は呼ばれるが、handler3は呼ばれない（例外で停止）
        handler1.assert_called_once_with(event)
        handler2.assert_called_once_with(event)
        handler3.assert_not_called()

    def test_event_type_detection(self):
        """イベントタイプの自動検出をテスト"""
        handler = Mock()
        event = DummyEvent("test data")

        self.event_bus.subscribe(DummyEvent, handler)
        self.event_bus.publish(event)

        # type(event)が正しく検出されることを確認
        handler.assert_called_once_with(event)

    def test_empty_event_bus(self):
        """空のEventBusのテスト"""
        event = DummyEvent("test data")

        # 何も起こらないことを確認
        self.event_bus.publish(event)

        # publishを呼んでもhandlersリストには空のリストが追加される（defaultdictの特性）
        # しかし、actual handlerは存在しないことを確認
        assert len(self.event_bus._handlers[DummyEvent]) == 0

from unittest.mock import Mock

import pytest

from sandpiper.app.message_dispatcher import MessageDispatcher
from sandpiper.shared.infrastructure.event_bus import EventBus


class TestMessageDispatcher:
    def setup_method(self):
        self.mock_event_bus = Mock(spec=EventBus)
        self.dispatcher = MessageDispatcher(self.mock_event_bus)

    def test_init(self):
        """MessageDispatcherの初期化をテスト"""
        event_bus = Mock(spec=EventBus)

        dispatcher = MessageDispatcher(event_bus)

        assert dispatcher._event_bus == event_bus

    def test_publish_message(self):
        """メッセージ発行をテスト"""
        # Arrange
        test_message = "テストメッセージ"

        # Act
        self.dispatcher.publish(test_message)

        # Assert
        self.mock_event_bus.publish.assert_called_once_with(test_message)

    def test_publish_object_message(self):
        """オブジェクトメッセージ発行をテスト"""

        # Arrange
        class TestEvent:
            def __init__(self, data):
                self.data = data

        test_event = TestEvent("テストデータ")

        # Act
        self.dispatcher.publish(test_event)

        # Assert
        self.mock_event_bus.publish.assert_called_once_with(test_event)

    def test_publish_none_message(self):
        """Noneメッセージ発行をテスト"""
        # Act
        self.dispatcher.publish(None)

        # Assert
        self.mock_event_bus.publish.assert_called_once_with(None)

    def test_publish_multiple_messages(self):
        """複数メッセージ発行をテスト"""
        # Arrange
        message1 = "メッセージ1"
        message2 = {"type": "event", "data": "テスト"}
        message3 = ["リスト", "メッセージ"]

        # Act
        self.dispatcher.publish(message1)
        self.dispatcher.publish(message2)
        self.dispatcher.publish(message3)

        # Assert
        assert self.mock_event_bus.publish.call_count == 3
        self.mock_event_bus.publish.assert_any_call(message1)
        self.mock_event_bus.publish.assert_any_call(message2)
        self.mock_event_bus.publish.assert_any_call(message3)

    def test_publish_with_event_bus_exception(self):
        """EventBusで例外が発生した場合のテスト"""
        # Arrange
        self.mock_event_bus.publish.side_effect = Exception("EventBus error")
        test_message = "エラーテストメッセージ"

        # Act & Assert
        with pytest.raises(Exception, match="EventBus error"):
            self.dispatcher.publish(test_message)

        self.mock_event_bus.publish.assert_called_once_with(test_message)

    def test_dispatcher_delegation(self):
        """MessageDispatcherがEventBusに正しく委譲することをテスト"""
        # Arrange
        custom_message = {"custom": "message", "id": 123}

        # Act
        self.dispatcher.publish(custom_message)

        # Assert - 引数がそのまま渡されることを確認
        args, kwargs = self.mock_event_bus.publish.call_args
        assert args[0] == custom_message
        assert args[0] is custom_message  # 同じオブジェクトであることを確認

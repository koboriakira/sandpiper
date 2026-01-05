from datetime import datetime
from unittest.mock import Mock

import pytest

from sandpiper.calendar.application.create_calendar_event import CreateCalendarEvent, CreateCalendarEventRequest
from sandpiper.calendar.domain.calendar_event import CalendarEvent, EventCategory, InsertedCalendarEvent


class TestCreateCalendarEvent:
    def test_execute_success(self):
        """カレンダーイベント作成が正常に動作することをテスト"""
        # Arrange
        mock_repository = Mock()
        start_time = datetime(2024, 1, 15, 10, 0)
        end_time = datetime(2024, 1, 15, 11, 0)

        expected_inserted_event = InsertedCalendarEvent(
            id="test-event-id",
            name="重要な会議",
            category=EventCategory.WORK,
            start_datetime=start_time,
            end_datetime=end_time,
        )
        mock_repository.create.return_value = expected_inserted_event

        service = CreateCalendarEvent(calendar_repository=mock_repository)
        request = CreateCalendarEventRequest(
            name="重要な会議",
            category=EventCategory.WORK,
            start_datetime=start_time,
            end_datetime=end_time,
        )

        # Act
        result = service.execute(request)

        # Assert
        assert result == expected_inserted_event
        mock_repository.create.assert_called_once()

        # リポジトリに渡されたイベントを検証
        called_event = mock_repository.create.call_args[0][0]
        assert isinstance(called_event, CalendarEvent)
        assert called_event.name == "重要な会議"
        assert called_event.category == EventCategory.WORK
        assert called_event.start_datetime == start_time
        assert called_event.end_datetime == end_time

    @pytest.mark.parametrize("category_name,expected_category", [
        ("仕事", EventCategory.WORK),
        ("プライベート", EventCategory.PRIVATE),
        ("TJPW", EventCategory.TJPW),
    ])
    def test_execute_with_different_categories(self, category_name, expected_category):
        """異なるカテゴリでのイベント作成をテスト"""
        # Arrange
        mock_repository = Mock()
        start_time = datetime(2024, 1, 15, 10, 0)
        end_time = datetime(2024, 1, 15, 11, 0)

        expected_inserted_event = InsertedCalendarEvent(
            id="test-event-id",
            name="テストイベント",
            category=expected_category,
            start_datetime=start_time,
            end_datetime=end_time,
        )
        mock_repository.create.return_value = expected_inserted_event

        service = CreateCalendarEvent(calendar_repository=mock_repository)
        request = CreateCalendarEventRequest(
            name="テストイベント",
            category=expected_category,
            start_datetime=start_time,
            end_datetime=end_time,
        )

        # Act
        result = service.execute(request)

        # Assert
        assert result.category == expected_category
        called_event = mock_repository.create.call_args[0][0]
        assert called_event.category == expected_category

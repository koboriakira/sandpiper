from datetime import datetime
from unittest.mock import Mock, patch

import pytest
from fastapi.testclient import TestClient

from sandpiper.api import app
from sandpiper.calendar.domain.calendar_event import EventCategory, InsertedCalendarEvent


@pytest.fixture
def client():
    """テストクライアントを作成"""
    return TestClient(app)


class TestCalendarAPI:
    @patch('sandpiper.routers.dependency.deps.get_sandpiper_app')
    def test_create_calendar_event_success(self, mock_get_app, client):
        """カレンダーイベント作成APIが正常に動作することをテスト"""
        # Arrange
        start_time = datetime(2024, 1, 15, 10, 0)
        end_time = datetime(2024, 1, 15, 11, 0)

        mock_app = Mock()
        mock_create_calendar_event = Mock()
        mock_app.create_calendar_event = mock_create_calendar_event
        mock_get_app.return_value = mock_app

        expected_inserted_event = InsertedCalendarEvent(
            id="test-event-id",
            name="重要な会議",
            category=EventCategory.WORK,
            start_datetime=start_time,
            end_datetime=end_time,
        )
        mock_create_calendar_event.execute.return_value = expected_inserted_event

        request_data = {
            "name": "重要な会議",
            "category": "仕事",
            "start_datetime": start_time.isoformat(),
            "end_datetime": end_time.isoformat(),
        }

        # Act
        response = client.post("/api/notion/calendar", json=request_data)

        # Assert
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["id"] == "test-event-id"
        assert response_data["name"] == "重要な会議"
        assert response_data["category"] == "仕事"
        assert response_data["start_datetime"] == start_time.isoformat()
        assert response_data["end_datetime"] == end_time.isoformat()

        # サービスが正しく呼び出されたことを確認
        mock_create_calendar_event.execute.assert_called_once()

    @pytest.mark.parametrize("category", ["仕事", "プライベート", "TJPW"])
    @patch('sandpiper.routers.dependency.deps.get_sandpiper_app')
    def test_create_calendar_event_different_categories(self, mock_get_app, client, category):
        """異なるカテゴリでのAPIリクエストをテスト"""
        # Arrange
        start_time = datetime(2024, 1, 15, 10, 0)
        end_time = datetime(2024, 1, 15, 11, 0)

        mock_app = Mock()
        mock_create_calendar_event = Mock()
        mock_app.create_calendar_event = mock_create_calendar_event
        mock_get_app.return_value = mock_app

        category_enum = EventCategory(category)
        expected_inserted_event = InsertedCalendarEvent(
            id="test-event-id",
            name="テストイベント",
            category=category_enum,
            start_datetime=start_time,
            end_datetime=end_time,
        )
        mock_create_calendar_event.execute.return_value = expected_inserted_event

        request_data = {
            "name": "テストイベント",
            "category": category,
            "start_datetime": start_time.isoformat(),
            "end_datetime": end_time.isoformat(),
        }

        # Act
        response = client.post("/api/notion/calendar", json=request_data)

        # Assert
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["category"] == category

    @patch('sandpiper.routers.dependency.deps.get_sandpiper_app')
    def test_create_calendar_event_invalid_category(self, mock_get_app, client):
        """無効なカテゴリでのリクエストをテスト"""
        # Arrange
        start_time = datetime(2024, 1, 15, 10, 0)
        end_time = datetime(2024, 1, 15, 11, 0)

        mock_app = Mock()
        mock_get_app.return_value = mock_app

        request_data = {
            "name": "テストイベント",
            "category": "無効なカテゴリ",
            "start_datetime": start_time.isoformat(),
            "end_datetime": end_time.isoformat(),
        }

        # Act
        response = client.post("/api/notion/calendar", json=request_data)

        # Assert
        assert response.status_code == 422  # Validation Error

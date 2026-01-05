from datetime import datetime
from unittest.mock import Mock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from sandpiper.calendar.domain.calendar_event import EventCategory, InsertedCalendarEvent
from sandpiper.routers.notion import CreateCalendarEventApiRequest, router


@pytest.fixture
def mock_sandpiper_app():
    """モックのSandPiperAppを作成"""
    mock_app = Mock()
    mock_create_calendar_event = Mock()
    mock_app.create_calendar_event = mock_create_calendar_event
    return mock_app


@pytest.fixture
def test_app(mock_sandpiper_app):
    """テスト用FastAPIアプリを作成"""
    app = FastAPI()
    
    # 依存性注入を直接設定
    def get_test_app():
        return mock_sandpiper_app
    
    # 依存性をオーバーライド
    from sandpiper.routers.dependency.deps import get_sandpiper_app
    app.dependency_overrides[get_sandpiper_app] = get_test_app
    
    app.include_router(router, prefix="/api")
    return app


class TestCalendarAPI:
    def test_create_calendar_event_success(self, test_app, mock_sandpiper_app):
        """カレンダーイベント作成APIが正常に動作することをテスト"""
        # Arrange
        start_time = datetime(2024, 1, 15, 10, 0)
        end_time = datetime(2024, 1, 15, 11, 0)
        
        expected_inserted_event = InsertedCalendarEvent(
            id="test-event-id",
            name="重要な会議",
            category=EventCategory.WORK,
            start_datetime=start_time,
            end_datetime=end_time,
        )
        mock_sandpiper_app.create_calendar_event.execute.return_value = expected_inserted_event
        
        request_data = {
            "name": "重要な会議",
            "category": "仕事",
            "start_datetime": start_time.isoformat(),
            "end_datetime": end_time.isoformat(),
        }
        
        # Act
        with TestClient(test_app) as client:
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
        mock_sandpiper_app.create_calendar_event.execute.assert_called_once()

    @pytest.mark.parametrize("category", ["仕事", "プライベート", "TJPW"])
    def test_create_calendar_event_different_categories(self, test_app, mock_sandpiper_app, category):
        """異なるカテゴリでのAPIリクエストをテスト"""
        # Arrange
        start_time = datetime(2024, 1, 15, 10, 0)
        end_time = datetime(2024, 1, 15, 11, 0)
        
        category_enum = EventCategory(category)
        expected_inserted_event = InsertedCalendarEvent(
            id="test-event-id",
            name="テストイベント",
            category=category_enum,
            start_datetime=start_time,
            end_datetime=end_time,
        )
        mock_sandpiper_app.create_calendar_event.execute.return_value = expected_inserted_event
        
        request_data = {
            "name": "テストイベント",
            "category": category,
            "start_datetime": start_time.isoformat(),
            "end_datetime": end_time.isoformat(),
        }
        
        # Act
        with TestClient(test_app) as client:
            response = client.post("/api/notion/calendar", json=request_data)
        
        # Assert
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["category"] == category

    def test_create_calendar_event_invalid_category(self, test_app, mock_sandpiper_app):
        """無効なカテゴリでのリクエストをテスト"""
        # Arrange
        start_time = datetime(2024, 1, 15, 10, 0)
        end_time = datetime(2024, 1, 15, 11, 0)
        
        request_data = {
            "name": "テストイベント",
            "category": "無効なカテゴリ",
            "start_datetime": start_time.isoformat(),
            "end_datetime": end_time.isoformat(),
        }
        
        # Act
        with TestClient(test_app) as client:
            response = client.post("/api/notion/calendar", json=request_data)
        
        # Assert
        assert response.status_code == 422  # Validation Error
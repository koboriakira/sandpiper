"""Notion API関連のエンドポイント"""

from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from lotion import BasePage  # type: ignore[import-untyped]
from pydantic import BaseModel

from sandpiper.app.app import SandPiperApp
from sandpiper.calendar.application.create_calendar_event import CreateCalendarEventRequest
from sandpiper.calendar.application.delete_calendar_events import DeleteCalendarEventsRequest
from sandpiper.calendar.domain.calendar_event import EventCategory
from sandpiper.plan.infrastructure.notion_todo_repository import TodoPage
from sandpiper.routers.dependency.deps import get_sandpiper_app

router = APIRouter(
    prefix="/notion",
    tags=["notion"],
    # このルーターでは全エンドポイントでのverify_authorizationを実行しない
    # dependencies=[Depends(verify_authorization)],
)


class NotionWebhookRequest(BaseModel):
    source: dict[str, Any]
    data: dict[str, Any]


class CreateCalendarEventApiRequest(BaseModel):
    name: str
    category: str  # "仕事", "プライベート", "TJPW"
    start_datetime: datetime
    end_datetime: datetime


@router.post("/todo/start")
async def start_todo(
    request: NotionWebhookRequest,
    sandpiper_app: SandPiperApp = Depends(get_sandpiper_app),
) -> JSONResponse:
    """Todoタスクを開始する"""
    base_page = BasePage.from_data(request.data)
    sandpiper_app.start_todo.execute(page_id=base_page.id)
    return JSONResponse(content={"page_id": base_page.id})


@router.post("/todo/complete")
async def complete_todo(
    request: NotionWebhookRequest,
    sandpiper_app: SandPiperApp = Depends(get_sandpiper_app),
) -> JSONResponse:
    """Todoタスクを完了する"""
    base_page = BasePage.from_data(request.data)
    sandpiper_app.complete_todo.execute(page_id=base_page.id)
    return JSONResponse(content={"page_id": base_page.id})


@router.post("/calendar")
async def create_calendar_event(
    request: CreateCalendarEventApiRequest,
    sandpiper_app: SandPiperApp = Depends(get_sandpiper_app),
) -> JSONResponse:
    """カレンダーイベントを作成する"""
    try:
        event_category = EventCategory(request.category)
    except ValueError:
        return JSONResponse(
            status_code=422,
            content={"detail": f"Invalid category: {request.category}. Valid categories: 仕事, プライベート, TJPW"},
        )

    create_request = CreateCalendarEventRequest(
        name=request.name,
        category=event_category,
        start_datetime=request.start_datetime,
        end_datetime=request.end_datetime,
    )
    inserted_event = sandpiper_app.create_calendar_event.execute(create_request)
    return JSONResponse(
        content={
            "id": inserted_event.id,
            "name": inserted_event.name,
            "category": inserted_event.category.value,
            "start_datetime": inserted_event.start_datetime.isoformat(),
            "end_datetime": inserted_event.end_datetime.isoformat(),
        }
    )


@router.post("/todo/to_project")
async def todo_to_project(
    request: NotionWebhookRequest,
    sandpiper_app: SandPiperApp = Depends(get_sandpiper_app),  # noqa: ARG001
) -> JSONResponse:
    """TodoをProjectに変換する

    NotionからのWebhookリクエストを受け取り、TodoをProjectに変換する処理を実行します。
    現在はダミーの実装です。

    Args:
        request: Notion Webhookリクエスト
        sandpiper_app: SandPiper アプリケーション (現在は未使用)

    Returns:
        JSONResponse: 変換結果のレスポンス
    """
    # ダミーの実装: Webhookリクエストからpage_idを取得
    print("Received Notion webhook request for todo_to_project:", request.data)
    print("Full request data:", request.source)
    page = BasePage.from_data(request.data)
    todo = TodoPage.from_data(request.data)
    print("Todo details:", todo.to_domain())
    return JSONResponse(
        content={
            "page_id": page.id,
            "message": "Todo converted to project successfully",
        }
    )


@router.delete("/calendar/{date_str}")
async def delete_calendar_events(
    date_str: str,
    sandpiper_app: SandPiperApp = Depends(get_sandpiper_app),
) -> JSONResponse:
    """指定された日付のカレンダーイベントを削除する

    Args:
        date_str: 日付文字列 (YYYYMMDD形式)
    """
    # 日付文字列をパース (YYYYMMDD形式)
    try:
        if len(date_str) != 8:
            raise ValueError("Date string must be in YYYYMMDD format")
        year = int(date_str[:4])
        month = int(date_str[4:6])
        day = int(date_str[6:8])
        target_date = datetime(year, month, day).date()
    except (ValueError, IndexError) as e:
        raise HTTPException(
            status_code=422, detail=f"Invalid date format: {date_str}. Expected format: YYYYMMDD"
        ) from e

    delete_request = DeleteCalendarEventsRequest(target_date=target_date)
    result = sandpiper_app.delete_calendar_events.execute(delete_request)

    return JSONResponse(
        content={
            "deleted_count": result.deleted_count,
            "target_date": date_str,
        }
    )

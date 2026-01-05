"""Notion API関連のエンドポイント"""

from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from lotion import BasePage  # type: ignore[import-untyped]
from pydantic import BaseModel

from sandpiper.app.app import SandPiperApp
from sandpiper.calendar.application.create_calendar_event import CreateCalendarEventRequest
from sandpiper.calendar.domain.calendar_event import EventCategory
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
            content={"detail": f"Invalid category: {request.category}. Valid categories: 仕事, プライベート, TJPW"}
        )
    
    create_request = CreateCalendarEventRequest(
        name=request.name,
        category=event_category,
        start_datetime=request.start_datetime,
        end_datetime=request.end_datetime,
    )
    inserted_event = sandpiper_app.create_calendar_event.execute(create_request)
    return JSONResponse(content={
        "id": inserted_event.id,
        "name": inserted_event.name,
        "category": inserted_event.category.value,
        "start_datetime": inserted_event.start_datetime.isoformat(),
        "end_datetime": inserted_event.end_datetime.isoformat(),
    })

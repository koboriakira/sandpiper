"""Notion API関連のエンドポイント"""

import logging
from datetime import datetime
from typing import Any

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from fastapi.responses import JSONResponse
from lotion import BasePage
from pydantic import BaseModel

from sandpiper.app.app import SandPiperApp
from sandpiper.calendar.application.create_calendar_event import CreateCalendarEventRequest
from sandpiper.calendar.application.delete_calendar_events import DeleteCalendarEventsRequest
from sandpiper.calendar.domain.calendar_event import EventCategory
from sandpiper.clips.application.create_clip import CreateClipRequest
from sandpiper.routers.dependency.deps import get_sandpiper_app

logger = logging.getLogger(__name__)

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


class CreateClipApiRequest(BaseModel):
    url: str
    title: str | None = None


def _execute_start_todo(sandpiper_app: SandPiperApp, page_id: str) -> None:
    """バックグラウンドでTodo開始処理を実行する"""
    try:
        sandpiper_app.start_todo.execute(page_id=page_id)
        logger.info("Todo started successfully: %s", page_id)
    except Exception:
        logger.exception("Failed to start todo: %s", page_id)


def _execute_complete_todo(sandpiper_app: SandPiperApp, page_id: str) -> None:
    """バックグラウンドでTodo完了処理を実行する"""
    try:
        sandpiper_app.complete_todo.execute(page_id=page_id)
        logger.info("Todo completed successfully: %s", page_id)
    except Exception:
        logger.exception("Failed to complete todo: %s", page_id)


def _execute_convert_to_project(sandpiper_app: SandPiperApp, page_id: str) -> None:
    """バックグラウンドでTodo→Project変換処理を実行する"""
    try:
        sandpiper_app.convert_to_project.execute(page_id=page_id)
        logger.info("Todo converted to project successfully: %s", page_id)
    except Exception:
        logger.exception("Failed to convert todo to project: %s", page_id)


def _execute_handle_special_todo(sandpiper_app: SandPiperApp, page_id: str) -> None:
    """バックグラウンドで特殊Todo処理を実行する"""
    try:
        result = sandpiper_app.handle_special_todo.execute(page_id=page_id)
        if result.success:
            logger.info("Special todo handled successfully: %s (handler: %s)", page_id, result.handler_name)
        else:
            logger.warning("Special todo handler not found: %s - %s", page_id, result.message)
    except Exception:
        logger.exception("Failed to handle special todo: %s", page_id)


def _execute_override_section(sandpiper_app: SandPiperApp, page_id: str) -> None:
    """バックグラウンドでセクション上書き処理を実行する"""
    try:
        result = sandpiper_app.override_section_by_schedule.execute(page_id=page_id)
        logger.info(
            "Section overridden successfully: %s (%s -> %s)",
            page_id,
            result.old_section.value if result.old_section else "None",
            result.new_section.value,
        )
    except ValueError as e:
        logger.warning("Failed to override section: %s - %s", page_id, str(e))
    except Exception:
        logger.exception("Failed to override section: %s", page_id)


@router.post("/todo/start")
async def start_todo(
    request: NotionWebhookRequest,
    background_tasks: BackgroundTasks,
    sandpiper_app: SandPiperApp = Depends(get_sandpiper_app),
) -> JSONResponse:
    """Todoタスクを開始する(非同期処理)"""
    base_page = BasePage.from_data(request.data)
    background_tasks.add_task(_execute_start_todo, sandpiper_app, base_page.id)
    return JSONResponse(content={"page_id": base_page.id, "status": "accepted"})


@router.post("/todo/complete")
async def complete_todo(
    request: NotionWebhookRequest,
    background_tasks: BackgroundTasks,
    sandpiper_app: SandPiperApp = Depends(get_sandpiper_app),
) -> JSONResponse:
    """Todoタスクを完了する(非同期処理)"""
    base_page = BasePage.from_data(request.data)
    background_tasks.add_task(_execute_complete_todo, sandpiper_app, base_page.id)
    return JSONResponse(content={"page_id": base_page.id, "status": "accepted"})


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
    background_tasks: BackgroundTasks,
    sandpiper_app: SandPiperApp = Depends(get_sandpiper_app),
) -> JSONResponse:
    """TodoをProjectに変換する(非同期処理)

    NotionからのWebhookリクエストを受け取り、TodoをProjectに変換する処理を実行します。
    同名のProjectとProjectTaskを作成します。

    Args:
        request: Notion Webhookリクエスト
        background_tasks: バックグラウンドタスク
        sandpiper_app: SandPiper アプリケーション

    Returns:
        JSONResponse: 受付結果のレスポンス
    """
    base_page = BasePage.from_data(request.data)
    background_tasks.add_task(_execute_convert_to_project, sandpiper_app, base_page.id)
    return JSONResponse(content={"page_id": base_page.id, "status": "accepted"})


@router.post("/todo/special")
async def handle_special_todo(
    request: NotionWebhookRequest,
    background_tasks: BackgroundTasks,
    sandpiper_app: SandPiperApp = Depends(get_sandpiper_app),
) -> JSONResponse:
    """特定の名前のTODOに対して特殊処理を実行する(非同期処理)

    このエンドポイントは、TODOデータベースの「処理」ボタンプロパティが押されたときに
    Notion Webhookから呼び出されます。TODOのタイトルに応じて、対応するハンドラーが
    特殊な処理を実行します。

    対応するハンドラー:
        - 「明日のTODOリストを作成」: プロジェクトタスク、ルーチンタスク、
          サムデイリスト(「明日やる」フラグ付き)からTODOを自動生成

    NotionからのWebhookリクエストを受け取り、TODOの名前に応じた特殊処理を実行します。
    処理結果はバックグラウンドで実行され、ログに出力されます。

    Args:
        request: Notion Webhookリクエスト
        background_tasks: バックグラウンドタスク
        sandpiper_app: SandPiper アプリケーション

    Returns:
        JSONResponse: 受付結果のレスポンス
    """
    base_page = BasePage.from_data(request.data)
    background_tasks.add_task(_execute_handle_special_todo, sandpiper_app, base_page.id)
    return JSONResponse(content={"page_id": base_page.id, "status": "accepted"})


@router.post("/archive")
async def archive_deleted_pages(
    sandpiper_app: SandPiperApp = Depends(get_sandpiper_app),
) -> JSONResponse:
    """論理削除されたページを物理削除する

    論理削除プロパティを持つデータベースから、
    論理削除プロパティが有効なページを物理削除します。

    Returns:
        JSONResponse: データベースごとの削除件数と合計
    """
    result = sandpiper_app.archive_deleted_pages.execute()
    return JSONResponse(
        content={
            "deleted_counts": result.deleted_counts,
            "total_deleted_count": result.total_deleted_count,
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


@router.post("/clips")
async def create_clip(
    request: CreateClipApiRequest,
    sandpiper_app: SandPiperApp = Depends(get_sandpiper_app),
) -> JSONResponse:
    """Clipを作成する

    Args:
        request: Clipの作成リクエスト(title, url)
        sandpiper_app: SandPiper アプリケーション

    Returns:
        JSONResponse: 作成されたClipの情報
    """
    create_request = CreateClipRequest(title=request.title, url=request.url)
    inserted_clip = sandpiper_app.create_clip.execute(create_request)
    return JSONResponse(
        content={
            "id": inserted_clip.id,
            "title": inserted_clip.title,
            "url": inserted_clip.url,
            "inbox_type": inserted_clip.inbox_type.value,
        }
    )


@router.post("/todo/override-section")
async def override_section_by_schedule(
    request: NotionWebhookRequest,
    background_tasks: BackgroundTasks,
    sandpiper_app: SandPiperApp = Depends(get_sandpiper_app),
) -> JSONResponse:
    """TODOの予定開始時刻からセクションを上書きする(非同期処理)

    NotionからのWebhookリクエストを受け取り、TODOの「予定」プロパティの
    開始時刻からセクションを計算して上書きします。

    Args:
        request: Notion Webhookリクエスト
        background_tasks: バックグラウンドタスク
        sandpiper_app: SandPiper アプリケーション

    Returns:
        JSONResponse: 受付結果のレスポンス
    """
    base_page = BasePage.from_data(request.data)
    background_tasks.add_task(_execute_override_section, sandpiper_app, base_page.id)
    return JSONResponse(content={"page_id": base_page.id, "status": "accepted"})

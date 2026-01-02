"""Notion API関連のエンドポイント"""

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from lotion import BasePage
from pydantic import BaseModel

from sandpiper.app.app import SandPiperApp
from sandpiper.routers.dependency.deps import get_sandpiper_app

router = APIRouter(
    prefix="/notion",
    tags=["notion"],
    # このルーターでは全エンドポイントでのverify_authorizationを実行しない
    # dependencies=[Depends(verify_authorization)],
)


class NotionWebhookRequest(BaseModel):
    source: dict
    data: dict


@router.post("/todo/start")
async def start_todo(
    request: NotionWebhookRequest,
    sandpiper_app: SandPiperApp = Depends(get_sandpiper_app),
) -> JSONResponse:
    """Todoタスクを開始する"""
    base_page = BasePage.from_data(request.data)
    sandpiper_app.start_todo.execute(page_id=base_page.id)
    return JSONResponse(content={"page_id": base_page.id})

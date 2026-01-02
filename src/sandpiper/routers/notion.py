"""Notion API関連のエンドポイント"""

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from sandpiper.routers.dependency.deps import get_sandpiper_app
from sandpiper.routers.dependency.verify_authorization import verify_authorization

# このルーターの全エンドポイントでverify_authorizationを実行
router = APIRouter(
    prefix="/notion",
    tags=["notion"],
    dependencies=[Depends(verify_authorization)],
)


class DatabaseListResponse(BaseModel):
    """データベース一覧レスポンス"""

    databases: list[str] = Field(..., description="データベース名のリスト")


class PageResponse(BaseModel):
    """ページ情報レスポンス"""

    page_id: str = Field(..., description="ページID")
    title: str = Field(..., description="ページタイトル")


@router.get("/databases", response_model=DatabaseListResponse)
async def list_databases(sandpiper_app=Depends(get_sandpiper_app)) -> JSONResponse:
    """Notionデータベース一覧を取得(ダミー実装)

    このエンドポイントはルーターレベルのdependencyにより
    自動的に認証チェックが行われます。
    """
    print(sandpiper_app)
    return JSONResponse(content={"databases": ["Database 1", "Database 2", "Database 3"]})


@router.get("/pages/{page_id}", response_model=PageResponse)
async def get_page(page_id: str) -> JSONResponse:
    """Notionページ情報を取得（ダミー実装）

    Args:
        page_id: 取得するページのID

    このエンドポイントはルーターレベルのdependencyにより
    自動的に認証チェックが行われます。
    """
    return JSONResponse(content={"page_id": page_id, "title": f"Page {page_id}"})


@router.post("/pages")
async def create_page(title: str) -> JSONResponse:
    """Notionページを作成（ダミー実装）

    Args:
        title: 作成するページのタイトル

    このエンドポイントはルーターレベルのdependencyにより
    自動的に認証チェックが行われます。
    """
    return JSONResponse(content={"page_id": "new_page_123", "title": title, "created": True})

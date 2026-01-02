"""挨拶APIルーター"""

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

router = APIRouter()


class VersionResponse(BaseModel):
    """バージョン情報レスポンス"""

    version: str = Field(..., description="アプリケーションのバージョン")
    python_version: str = Field(..., description="Pythonのバージョン")


@router.get("/version", response_model=VersionResponse)
async def health() -> JSONResponse:
    from sandpiper import __version__

    """ヘルスチェックエンドポイント"""
    return JSONResponse(content={"status": "healthy", "version": __version__})

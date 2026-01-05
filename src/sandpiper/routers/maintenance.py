"""メンテナンス関連のエンドポイント"""

from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter(
    prefix="/maintenance",
    tags=["maintenance"],
    # このルーターでは全エンドポイントでのverify_authorizationを実行しない
    # dependencies=[Depends(verify_authorization)],
)


@router.post("")
async def maintenance() -> JSONResponse:
    """メンテナンス用エンドポイント(処理なし)"""
    return JSONResponse(content={"status": "received"})

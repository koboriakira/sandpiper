"""FastAPIアプリケーション"""

import json
import os
from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.responses import Response, StreamingResponse

from sandpiper.app.app import bootstrap

from . import __version__
from .routers import health, maintenance, notion

# 環境設定
ENVIRONMENT = os.getenv("ENVIRONMENT", "production")  # デフォルトは本番環境
DEBUG = os.getenv("DEBUG", "false").lower() in ("true", "1", "yes")
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "").split(",") if os.getenv("ALLOWED_ORIGINS") else []

# 開発環境判定
IS_DEVELOPMENT = ENVIRONMENT.lower() in ("development", "dev", "local") or DEBUG

if IS_DEVELOPMENT:
    print("⚙️ .envファイルから環境変数を読み込み")
    load_dotenv()


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """アプリケーションライフサイクル管理"""
    # 起動時の処理
    env_label = "開発環境" if IS_DEVELOPMENT else "本番環境"
    print(f"🚀 FastAPIアプリケーション起動 [{env_label}]")
    if IS_DEVELOPMENT:
        print("⚠️  開発モード: セキュリティ制限が緩和されています")
    print("設定中のSandpiperアプリケーションを初期化...")
    app.state.sandpiper_app = bootstrap()
    print("Sandpiperアプリケーションの初期化が完了しました")

    # yieldは非同期コンテキストマネージャーの境界線
    # yieldより前: アプリケーション起動時に1回だけ実行される処理(初期化)
    # yieldより後: アプリケーション終了時に1回だけ実行される処理(クリーンアップ)
    # yield中: アプリケーションが稼働している期間(リクエストを受け付ける)
    yield

    # 終了時の処理
    print("👋 FastAPIアプリケーション終了")


# FastAPIアプリケーション作成
app = FastAPI(
    title="Python Project 2026 API",
    description="2026年の最新Python開発テンプレート - FastAPI版",
    version=__version__,
    lifespan=lifespan,
    # 本番環境ではドキュメントを無効化(オプション)
    docs_url="/docs" if IS_DEVELOPMENT else None,
    redoc_url="/redoc" if IS_DEVELOPMENT else None,
    openapi_url="/openapi.json" if IS_DEVELOPMENT else None,
)

# CORS設定(環境に応じて切り替え)
if IS_DEVELOPMENT:
    # 開発環境: すべてのオリジンを許可
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    # 本番環境: 指定されたオリジンのみ許可
    if not ALLOWED_ORIGINS:
        # 環境変数が設定されていない場合のフォールバック
        print("⚠️  警告: ALLOWED_ORIGINSが設定されていません。CORSは無効化されます。")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
        allow_headers=["Content-Type", "Authorization"],
    )


# レスポンスログ出力ミドルウェア
@app.middleware("http")
async def log_response(
    request: Request, call_next: Callable[[Request], Awaitable[StreamingResponse]]
) -> Response:
    """レスポンスをログ出力するミドルウェア"""
    response: StreamingResponse = await call_next(request)

    # レスポンスボディを取得
    body_bytes = b""
    async for chunk in response.body_iterator:
        if isinstance(chunk, bytes):
            body_bytes += chunk
        elif isinstance(chunk, str):
            body_bytes += chunk.encode()
        else:
            body_bytes += bytes(chunk)

    # ログ出力
    print(f"📤 Response: {request.method} {request.url.path} -> {response.status_code}")
    try:
        body_dict = json.loads(body_bytes)
        print(json.dumps(body_dict, ensure_ascii=False, indent=2))
    except Exception:
        print(body_bytes.decode())

    # 新しいレスポンスを作成して返却
    return Response(
        content=body_bytes,
        status_code=response.status_code,
        headers=dict(response.headers),
        media_type=response.media_type,
    )


@app.get("/", tags=["Root"])
async def root() -> JSONResponse:
    """ルートエンドポイント"""
    return JSONResponse(
        content={
            "message": "Python Project 2026 API",
            "version": __version__,
            "environment": ENVIRONMENT,
            "docs": "/docs" if IS_DEVELOPMENT else None,
            "redoc": "/redoc" if IS_DEVELOPMENT else None,
        }
    )


# ルーターを登録
app.include_router(health.router, prefix="/api", tags=["Health"])
app.include_router(notion.router, prefix="/api", tags=["Notion"])
app.include_router(maintenance.router, prefix="/api", tags=["Maintenance"])

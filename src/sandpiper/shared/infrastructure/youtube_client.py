"""YouTube Data API v3 クライアント"""

import re
from pathlib import Path
from typing import Any

from google.oauth2 import service_account
from googleapiclient.discovery import build  # type: ignore[import-untyped]
from googleapiclient.errors import HttpError  # type: ignore[import-untyped]

# サービスアカウントファイルの検索パス(優先順位順)
SERVICE_ACCOUNT_PATHS = [
    Path("google-service-account.json"),  # プロジェクトルート
    Path("/etc/secrets/google-service-account.json"),  # コンテナ環境
]


def _find_service_account_file() -> Path | None:
    """サービスアカウントファイルを検索する"""
    for path in SERVICE_ACCOUNT_PATHS:
        if path.exists():
            return path
    return None


def _extract_video_id(url: str) -> str | None:
    """YouTubeのURLから動画IDを抽出する

    対応URL形式:
    - https://www.youtube.com/watch?v=VIDEO_ID
    - https://youtu.be/VIDEO_ID
    - https://www.youtube.com/embed/VIDEO_ID
    - https://www.youtube.com/v/VIDEO_ID
    - https://www.youtube.com/shorts/VIDEO_ID
    """
    patterns = [
        r"(?:youtube\.com/watch\?v=|youtube\.com/watch\?.+&v=)([a-zA-Z0-9_-]{11})",
        r"youtu\.be/([a-zA-Z0-9_-]{11})",
        r"youtube\.com/embed/([a-zA-Z0-9_-]{11})",
        r"youtube\.com/v/([a-zA-Z0-9_-]{11})",
        r"youtube\.com/shorts/([a-zA-Z0-9_-]{11})",
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)

    return None


class YouTubeClient:
    """YouTube Data API v3のラッパークラス - 動画情報の取得を提供"""

    def __init__(self, service_account_file: Path | None = None) -> None:
        """
        YouTubeクライアントを初期化

        Args:
            service_account_file: サービスアカウントJSONファイルのパス
                                 (省略時は自動検索)

        Raises:
            FileNotFoundError: サービスアカウントファイルが見つからない場合
        """
        if service_account_file is None:
            service_account_file = _find_service_account_file()

        if service_account_file is None:
            msg = "Service account file not found. Place google-service-account.json in project root or /etc/secrets/"
            raise FileNotFoundError(msg)

        self._service_account_file = service_account_file
        self._service = self._build_service()

    def _build_service(self) -> Any:
        """YouTube APIサービスを構築する"""
        credentials = service_account.Credentials.from_service_account_file(  # type: ignore[no-untyped-call]
            str(self._service_account_file),
            scopes=["https://www.googleapis.com/auth/youtube.readonly"],
        )
        return build("youtube", "v3", credentials=credentials)

    def get_video_title(self, url: str) -> str | None:
        """
        YouTube動画のタイトルを取得する

        Args:
            url: YouTube動画のURL

        Returns:
            動画タイトル。取得失敗時はNone
        """
        video_id = _extract_video_id(url)
        if video_id is None:
            return None

        try:
            response = self._service.videos().list(part="snippet", id=video_id).execute()

            items = response.get("items", [])
            if items:
                return str(items[0]["snippet"]["title"])

            return None

        except HttpError:
            return None
        except Exception:
            return None

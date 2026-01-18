import re
from dataclasses import dataclass

import httpx

from sandpiper.clips.domain.clip import Clip, InsertedClip
from sandpiper.clips.domain.clips_repository import ClipsRepository
from sandpiper.shared.infrastructure.youtube_client import YouTubeClient
from sandpiper.shared.notion.databases.inbox import InboxType

DEFAULT_TITLE = "タイトル取得不能"


def _is_youtube_url(url: str) -> bool:
    """URLがYouTubeのURLかどうかを判定する"""
    return "youtube.com" in url or "youtu.be" in url


def fetch_youtube_title(url: str) -> str | None:
    """YouTube Data API v3を使用して動画タイトルを取得する

    Args:
        url: YouTube動画のURL

    Returns:
        動画タイトル。取得できない場合はNone
    """
    try:
        client = YouTubeClient()
        return client.get_video_title(url)
    except FileNotFoundError:
        # サービスアカウントファイルが見つからない場合
        return None
    except Exception:
        # その他のエラー
        return None


def fetch_page_title(url: str, timeout: float = 10.0) -> str | None:
    """指定されたURLのページタイトルを取得する

    Args:
        url: 取得対象のURL
        timeout: タイムアウト秒数 (デフォルト: 10.0)

    Returns:
        ページのタイトル文字列。取得できない場合はNone
    """
    try:
        response = httpx.get(url, timeout=timeout, follow_redirects=True)
        response.raise_for_status()

        html_content = response.text
        match = re.search(r"<title[^>]*>(.*?)</title>", html_content, re.IGNORECASE | re.DOTALL)

        if match:
            title = match.group(1).strip()
            # HTMLエンティティをデコード
            title = title.replace("&amp;", "&")
            title = title.replace("&lt;", "<")
            title = title.replace("&gt;", ">")
            title = title.replace("&quot;", '"')
            title = title.replace("&#39;", "'")
            # 改行やタブを空白に置換
            title = re.sub(r"\s+", " ", title)
            return title

        return None
    except (httpx.HTTPError, Exception):
        return None


@dataclass
class CreateClipRequest:
    url: str
    title: str | None = None


@dataclass
class CreateClip:
    _clips_repository: ClipsRepository

    def __init__(self, clips_repository: ClipsRepository) -> None:
        self._clips_repository = clips_repository

    def execute(self, request: CreateClipRequest) -> InsertedClip:
        title = request.title
        inbox_type = InboxType.from_url(request.url)

        if title is None:
            # YouTube URLの場合はYouTube Data API v3でタイトルを取得
            title = fetch_youtube_title(request.url) if _is_youtube_url(request.url) else fetch_page_title(request.url)
            if title is None:
                title = DEFAULT_TITLE

        # タイトルが取得できなかった場合のみ、自動取得フラグを立てる
        auto_fetch_title = title == DEFAULT_TITLE

        clip = Clip(title=title, url=request.url, inbox_type=inbox_type, auto_fetch_title=auto_fetch_title)
        inserted_clip = self._clips_repository.save(clip)
        print(f"Created Clip: {inserted_clip}")
        return inserted_clip

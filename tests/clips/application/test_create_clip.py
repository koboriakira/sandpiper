"""CreateClipユースケースのテスト"""

from unittest.mock import MagicMock, patch

import pytest

from sandpiper.clips.application.create_clip import (
    DEFAULT_TITLE,
    CreateClip,
    CreateClipRequest,
    _is_youtube_url,
    fetch_youtube_title,
)
from sandpiper.clips.domain.clip import Clip, InsertedClip
from sandpiper.clips.domain.clips_repository import ClipsRepository
from sandpiper.shared.notion.databases.inbox import InboxType


class TestIsYouTubeUrl:
    """YouTube URL判定のテスト"""

    @pytest.mark.parametrize(
        "url",
        [
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "https://youtu.be/dQw4w9WgXcQ",
            "https://youtube.com/watch?v=dQw4w9WgXcQ",
            "http://www.youtube.com/embed/dQw4w9WgXcQ",
        ],
    )
    def test_youtube_url_returns_true(self, url: str):
        """YouTube URLはTrueを返す"""
        assert _is_youtube_url(url) is True

    @pytest.mark.parametrize(
        "url",
        [
            "https://www.google.com",
            "https://example.com",
            "https://vimeo.com/12345",
            "https://twitter.com/user/status/12345",
        ],
    )
    def test_non_youtube_url_returns_false(self, url: str):
        """非YouTube URLはFalseを返す"""
        assert _is_youtube_url(url) is False


class TestFetchYouTubeTitle:
    """YouTube APIを使ったタイトル取得のテスト"""

    def test_success(self):
        """正常にタイトルを取得できる"""
        mock_client = MagicMock()
        mock_client.get_video_title.return_value = "Test Video Title"

        with patch(
            "sandpiper.clips.application.create_clip.YouTubeClient",
            return_value=mock_client,
        ):
            title = fetch_youtube_title("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
            assert title == "Test Video Title"

    def test_service_account_not_found(self):
        """サービスアカウントファイルがない場合はNone"""
        with patch(
            "sandpiper.clips.application.create_clip.YouTubeClient",
            side_effect=FileNotFoundError("Service account file not found"),
        ):
            title = fetch_youtube_title("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
            assert title is None

    def test_api_error(self):
        """APIエラーの場合はNone"""
        with patch(
            "sandpiper.clips.application.create_clip.YouTubeClient",
            side_effect=Exception("API Error"),
        ):
            title = fetch_youtube_title("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
            assert title is None


class MockClipsRepository(ClipsRepository):
    """テスト用のClipsRepositoryモック"""

    def __init__(self):
        self.saved_clips: list[Clip] = []

    def save(self, clip: Clip) -> InsertedClip:
        self.saved_clips.append(clip)
        return InsertedClip(
            id="test-id",
            title=clip.title,
            url=clip.url,
            inbox_type=clip.inbox_type,
            auto_fetch_title=clip.auto_fetch_title,
        )


class TestCreateClip:
    """CreateClipユースケースのテスト"""

    def setup_method(self):
        self.repository = MockClipsRepository()
        self.use_case = CreateClip(clips_repository=self.repository)

    def test_create_clip_with_explicit_title(self):
        """明示的にタイトルを指定した場合"""
        request = CreateClipRequest(
            url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            title="My Custom Title",
        )

        result = self.use_case.execute(request)

        assert result.title == "My Custom Title"
        assert result.url == "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        assert result.inbox_type == InboxType.VIDEO
        assert result.auto_fetch_title is False  # タイトル指定済みなのでFalse

    def test_create_clip_youtube_url_api_success(self):
        """YouTube URLでAPI取得成功の場合"""
        mock_client = MagicMock()
        mock_client.get_video_title.return_value = "YouTube Video Title"

        with patch(
            "sandpiper.clips.application.create_clip.YouTubeClient",
            return_value=mock_client,
        ):
            request = CreateClipRequest(url="https://www.youtube.com/watch?v=dQw4w9WgXcQ")
            result = self.use_case.execute(request)

        assert result.title == "YouTube Video Title"
        assert result.inbox_type == InboxType.VIDEO
        assert result.auto_fetch_title is False  # タイトル取得成功なのでFalse

    def test_create_clip_youtube_url_api_failure(self):
        """YouTube URLでAPI取得失敗の場合"""
        with patch(
            "sandpiper.clips.application.create_clip.YouTubeClient",
            side_effect=FileNotFoundError("Service account file not found"),
        ):
            request = CreateClipRequest(url="https://www.youtube.com/watch?v=dQw4w9WgXcQ")
            result = self.use_case.execute(request)

        assert result.title == DEFAULT_TITLE
        assert result.inbox_type == InboxType.VIDEO
        assert result.auto_fetch_title is True  # タイトル取得失敗なのでTrue

    def test_create_clip_non_youtube_url(self):
        """非YouTube URLの場合はHTMLタイトル取得"""
        with patch(
            "sandpiper.clips.application.create_clip.fetch_page_title",
            return_value="Web Page Title",
        ):
            request = CreateClipRequest(url="https://example.com/article")
            result = self.use_case.execute(request)

        assert result.title == "Web Page Title"
        assert result.inbox_type == InboxType.WEB
        assert result.auto_fetch_title is False

    def test_create_clip_non_youtube_url_fetch_failure(self):
        """非YouTube URLでタイトル取得失敗の場合"""
        with patch(
            "sandpiper.clips.application.create_clip.fetch_page_title",
            return_value=None,
        ):
            request = CreateClipRequest(url="https://example.com/article")
            result = self.use_case.execute(request)

        assert result.title == DEFAULT_TITLE
        assert result.inbox_type == InboxType.WEB
        assert result.auto_fetch_title is True

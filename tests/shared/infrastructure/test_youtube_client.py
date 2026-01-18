"""YouTube Data API v3 クライアントのテスト"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from sandpiper.shared.infrastructure.youtube_client import (
    YouTubeClient,
    _extract_video_id,
    _find_service_account_file,
)


class TestExtractVideoId:
    """動画ID抽出のテスト"""

    @pytest.mark.parametrize(
        ("url", "expected"),
        [
            ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "dQw4w9WgXcQ"),
            ("https://youtu.be/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
            ("https://www.youtube.com/embed/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
            ("https://www.youtube.com/v/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
            ("https://www.youtube.com/shorts/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
            ("https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=123", "dQw4w9WgXcQ"),
            ("https://www.youtube.com/watch?list=PLxyz&v=dQw4w9WgXcQ", "dQw4w9WgXcQ"),
        ],
    )
    def test_extract_video_id_success(self, url: str, expected: str):
        """各種YouTube URL形式から正しく動画IDを抽出できる"""
        assert _extract_video_id(url) == expected

    @pytest.mark.parametrize(
        "url",
        [
            "https://www.google.com",
            "https://example.com/watch?v=test",
            "https://youtube.com/channel/UCxxx",
            "invalid_url",
            "",
        ],
    )
    def test_extract_video_id_failure(self, url: str):
        """YouTube動画URL以外からはNoneを返す"""
        assert _extract_video_id(url) is None


class TestFindServiceAccountFile:
    """サービスアカウントファイル検索のテスト"""

    def test_find_project_root_file(self, tmp_path: Path, monkeypatch):
        """プロジェクトルートのファイルを優先して検出"""
        # カレントディレクトリを一時ディレクトリに変更
        monkeypatch.chdir(tmp_path)

        # テスト用ファイル作成
        service_account_file = tmp_path / "google-service-account.json"
        service_account_file.write_text("{}")

        # SERVICE_ACCOUNT_PATHSをモック
        with patch(
            "sandpiper.shared.infrastructure.youtube_client.SERVICE_ACCOUNT_PATHS",
            [service_account_file, Path("/etc/secrets/google-service-account.json")],
        ):
            result = _find_service_account_file()
            assert result == service_account_file

    def test_find_etc_secrets_file(self, tmp_path: Path, monkeypatch):
        """プロジェクトルートになければ/etc/secrets/を検出"""
        monkeypatch.chdir(tmp_path)

        # /etc/secrets相当のパスをテスト用に作成
        secrets_dir = tmp_path / "etc" / "secrets"
        secrets_dir.mkdir(parents=True)
        service_account_file = secrets_dir / "google-service-account.json"
        service_account_file.write_text("{}")

        # SERVICE_ACCOUNT_PATHSをモック
        with patch(
            "sandpiper.shared.infrastructure.youtube_client.SERVICE_ACCOUNT_PATHS",
            [tmp_path / "google-service-account.json", service_account_file],
        ):
            result = _find_service_account_file()
            assert result == service_account_file

    def test_find_no_file(self, tmp_path: Path, monkeypatch):
        """ファイルがない場合はNoneを返す"""
        monkeypatch.chdir(tmp_path)

        with patch(
            "sandpiper.shared.infrastructure.youtube_client.SERVICE_ACCOUNT_PATHS",
            [tmp_path / "nonexistent.json"],
        ):
            result = _find_service_account_file()
            assert result is None


class TestYouTubeClient:
    """YouTubeClientのテスト"""

    def test_init_file_not_found(self, tmp_path: Path, monkeypatch):
        """サービスアカウントファイルがない場合はFileNotFoundError"""
        monkeypatch.chdir(tmp_path)

        with (
            patch(
                "sandpiper.shared.infrastructure.youtube_client.SERVICE_ACCOUNT_PATHS",
                [tmp_path / "nonexistent.json"],
            ),
            pytest.raises(FileNotFoundError, match="Service account file not found"),
        ):
            YouTubeClient()

    def test_init_with_explicit_path(self, tmp_path: Path):
        """明示的にパスを指定した場合はそのパスを使用"""
        service_account_file = tmp_path / "service-account.json"
        service_account_file.write_text('{"type": "service_account"}')

        with (
            patch(
                "sandpiper.shared.infrastructure.youtube_client.service_account.Credentials.from_service_account_file"
            ) as mock_creds,
            patch("sandpiper.shared.infrastructure.youtube_client.build"),
        ):
            mock_creds.return_value = MagicMock()
            client = YouTubeClient(service_account_file=service_account_file)
            assert client._service_account_file == service_account_file

    def test_get_video_title_success(self, tmp_path: Path):
        """動画タイトルの取得成功"""
        service_account_file = tmp_path / "service-account.json"
        service_account_file.write_text('{"type": "service_account"}')

        mock_service = MagicMock()
        mock_service.videos().list().execute.return_value = {"items": [{"snippet": {"title": "Test Video Title"}}]}

        with (
            patch(
                "sandpiper.shared.infrastructure.youtube_client.service_account.Credentials.from_service_account_file"
            ),
            patch(
                "sandpiper.shared.infrastructure.youtube_client.build",
                return_value=mock_service,
            ),
        ):
            client = YouTubeClient(service_account_file=service_account_file)
            title = client.get_video_title("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
            assert title == "Test Video Title"

    def test_get_video_title_not_found(self, tmp_path: Path):
        """動画が見つからない場合はNone"""
        service_account_file = tmp_path / "service-account.json"
        service_account_file.write_text('{"type": "service_account"}')

        mock_service = MagicMock()
        mock_service.videos().list().execute.return_value = {"items": []}

        with (
            patch(
                "sandpiper.shared.infrastructure.youtube_client.service_account.Credentials.from_service_account_file"
            ),
            patch(
                "sandpiper.shared.infrastructure.youtube_client.build",
                return_value=mock_service,
            ),
        ):
            client = YouTubeClient(service_account_file=service_account_file)
            title = client.get_video_title("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
            assert title is None

    def test_get_video_title_invalid_url(self, tmp_path: Path):
        """無効なURLの場合はNone"""
        service_account_file = tmp_path / "service-account.json"
        service_account_file.write_text('{"type": "service_account"}')

        with (
            patch(
                "sandpiper.shared.infrastructure.youtube_client.service_account.Credentials.from_service_account_file"
            ),
            patch("sandpiper.shared.infrastructure.youtube_client.build"),
        ):
            client = YouTubeClient(service_account_file=service_account_file)
            title = client.get_video_title("https://www.google.com")
            assert title is None

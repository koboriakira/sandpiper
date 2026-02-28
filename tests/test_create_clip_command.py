"""create-clip CLIコマンドのテスト"""

import sys
from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from sandpiper.clips.domain.clip import InsertedClip
from sandpiper.shared.notion.databases.inbox import InboxType


@patch.dict("os.environ", {"GITHUB_TOKEN": "test_token", "NOTION_SECRET": "test_NOTION_SECRET"})
def get_runner_and_app():
    """テスト用のrunnerとappを取得する"""
    modules_to_remove = [key for key in sys.modules if key.startswith("sandpiper")]
    for module in modules_to_remove:
        del sys.modules[module]

    with patch("sandpiper.app.app.bootstrap") as mock_bootstrap:
        mock_app = MagicMock()
        mock_bootstrap.return_value = mock_app

        from sandpiper.main import app

        return CliRunner(), app, mock_app


class TestCreateClipCommand:
    def setup_method(self):
        """各テストの前にrunner、app、mock_appを取得"""
        self.runner, self.app, self.mock_sandpiper_app = get_runner_and_app()

    def test_help_shows_description(self):
        """--helpでコマンドの説明が表示されること"""
        result = self.runner.invoke(self.app, ["create-clip", "--help"])
        assert result.exit_code == 0
        assert "Clip" in result.stdout or "クリップ" in result.stdout

    def test_create_clip_with_url_only(self):
        """URLのみ指定してClipを作成できること"""
        self.mock_sandpiper_app.create_clip.execute.return_value = InsertedClip(
            id="clip-page-id",
            title="Example Page",
            url="https://example.com/article",
            inbox_type=InboxType.WEB,
        )

        result = self.runner.invoke(self.app, ["create-clip", "https://example.com/article"])
        assert result.exit_code == 0
        assert "Example Page" in result.stdout

        # create_clipが正しい引数で呼ばれたことを確認
        self.mock_sandpiper_app.create_clip.execute.assert_called_once()
        call_args = self.mock_sandpiper_app.create_clip.execute.call_args[0][0]
        assert call_args.url == "https://example.com/article"
        assert call_args.title is None

    def test_create_clip_with_title(self):
        """--titleオプションでタイトルを指定できること"""
        self.mock_sandpiper_app.create_clip.execute.return_value = InsertedClip(
            id="clip-page-id",
            title="カスタムタイトル",
            url="https://example.com/article",
            inbox_type=InboxType.WEB,
        )

        result = self.runner.invoke(
            self.app, ["create-clip", "https://example.com/article", "--title", "カスタムタイトル"]
        )
        assert result.exit_code == 0
        assert "カスタムタイトル" in result.stdout

        call_args = self.mock_sandpiper_app.create_clip.execute.call_args[0][0]
        assert call_args.url == "https://example.com/article"
        assert call_args.title == "カスタムタイトル"

    def test_create_clip_shows_clip_info(self):
        """作成成功時にClipの情報が表示されること"""
        self.mock_sandpiper_app.create_clip.execute.return_value = InsertedClip(
            id="clip-page-id",
            title="Test Article",
            url="https://example.com/test",
            inbox_type=InboxType.WEB,
        )

        result = self.runner.invoke(self.app, ["create-clip", "https://example.com/test"])
        assert result.exit_code == 0
        assert "Test Article" in result.stdout
        assert "https://example.com/test" in result.stdout

    def test_create_clip_youtube_url(self):
        """YouTube URLでClipを作成できること"""
        self.mock_sandpiper_app.create_clip.execute.return_value = InsertedClip(
            id="clip-page-id",
            title="YouTube Video",
            url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            inbox_type=InboxType.VIDEO,
        )

        result = self.runner.invoke(self.app, ["create-clip", "https://www.youtube.com/watch?v=dQw4w9WgXcQ"])
        assert result.exit_code == 0
        assert "YouTube Video" in result.stdout

    def test_create_clip_error_handling(self):
        """エラー発生時にエラーメッセージが表示されること"""
        self.mock_sandpiper_app.create_clip.execute.side_effect = Exception("API Error")

        result = self.runner.invoke(self.app, ["create-clip", "https://example.com/test"])
        assert result.exit_code == 1
        assert "エラー" in result.stdout

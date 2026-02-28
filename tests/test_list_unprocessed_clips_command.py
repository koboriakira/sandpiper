"""list-unprocessed-clips CLIコマンドのテスト"""

import sys
from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from sandpiper.clips.query.unprocessed_clip_item import UnprocessedClipItem


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


class TestListUnprocessedClipsCommand:
    def setup_method(self):
        """各テストの前にrunner、app、mock_appを取得"""
        self.runner, self.app, self.mock_sandpiper_app = get_runner_and_app()

    def test_help_shows_description(self):
        """--helpでコマンドの説明が表示されること"""
        result = self.runner.invoke(self.app, ["list-unprocessed-clips", "--help"])
        assert result.exit_code == 0
        assert "未処理" in result.stdout

    def test_list_unprocessed_clips_with_results(self):
        """未処理Clipsがある場合に一覧が表示されること"""
        self.mock_sandpiper_app.list_unprocessed_clips.execute.return_value = [
            UnprocessedClipItem(title="Pythonの新機能", url="https://example.com/python"),
            UnprocessedClipItem(title="TypeScript入門", url="https://example.com/ts"),
        ]

        result = self.runner.invoke(self.app, ["list-unprocessed-clips"])
        assert result.exit_code == 0
        assert "Pythonの新機能" in result.stdout
        assert "https://example.com/python" in result.stdout
        assert "TypeScript入門" in result.stdout
        assert "https://example.com/ts" in result.stdout

    def test_list_unprocessed_clips_empty(self):
        """未処理Clipsがない場合にメッセージが表示されること"""
        self.mock_sandpiper_app.list_unprocessed_clips.execute.return_value = []

        result = self.runner.invoke(self.app, ["list-unprocessed-clips"])
        assert result.exit_code == 0
        assert "ありません" in result.stdout

    def test_list_unprocessed_clips_shows_count(self):
        """未処理Clips件数が表示されること"""
        self.mock_sandpiper_app.list_unprocessed_clips.execute.return_value = [
            UnprocessedClipItem(title="記事1", url="https://example.com/1"),
            UnprocessedClipItem(title="記事2", url="https://example.com/2"),
            UnprocessedClipItem(title="記事3", url="https://example.com/3"),
        ]

        result = self.runner.invoke(self.app, ["list-unprocessed-clips"])
        assert result.exit_code == 0
        assert "3" in result.stdout

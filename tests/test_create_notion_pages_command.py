"""create-notion-pages CLIコマンドのテスト"""

import json
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from sandpiper.recipe.domain.recipe import InsertedRecipe


# テスト前にbootstrapをモックする必要がある
@patch.dict("os.environ", {"GITHUB_TOKEN": "test_token", "NOTION_TOKEN": "test_notion_token"})
def get_runner_and_app():
    """テスト用のrunnerとappを取得する"""
    # 既存のモジュールをクリア
    modules_to_remove = [key for key in sys.modules if key.startswith("sandpiper")]
    for module in modules_to_remove:
        del sys.modules[module]

    # モックを設定してからインポート
    with patch("sandpiper.app.app.bootstrap") as mock_bootstrap:
        mock_app = MagicMock()
        mock_bootstrap.return_value = mock_app

        from sandpiper.main import app

        return CliRunner(), app, mock_app


class TestCreateNotionPagesCommand:
    def setup_method(self):
        """各テストの前にrunner、app、mock_appを取得"""
        self.runner, self.app, self.mock_sandpiper_app = get_runner_and_app()

    def test_help_shows_description(self):
        """--helpでコマンドの説明が表示されること"""
        result = self.runner.invoke(self.app, ["create-notion-pages", "--help"])
        assert result.exit_code == 0
        assert "JSONファイルからNotionページを作成" in result.stdout

    def test_file_not_found(self):
        """存在しないファイルを指定した場合にエラーになること"""
        result = self.runner.invoke(self.app, ["create-notion-pages", "/nonexistent/path.json"])
        assert result.exit_code == 1
        assert "ファイルが見つかりません" in result.stdout

    def test_invalid_json_file(self):
        """無効なJSONファイルを指定した場合にエラーになること"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write("invalid json content")
            temp_path = f.name

        try:
            result = self.runner.invoke(self.app, ["create-notion-pages", temp_path])
            assert result.exit_code == 1
            assert "JSONファイルの解析に失敗" in result.stdout
        finally:
            Path(temp_path).unlink()

    def test_json_not_array(self):
        """JSONが配列でない場合にエラーになること"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump({"type": "Recipe", "title": "Test"}, f)
            temp_path = f.name

        try:
            result = self.runner.invoke(self.app, ["create-notion-pages", temp_path])
            assert result.exit_code == 1
            assert "配列形式である必要があります" in result.stdout
        finally:
            Path(temp_path).unlink()

    def test_skip_unsupported_type(self):
        """未対応のタイプはスキップされること"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump([{"type": "UnsupportedType", "title": "Test"}], f)
            temp_path = f.name

        try:
            result = self.runner.invoke(self.app, ["create-notion-pages", temp_path])
            assert result.exit_code == 0
            assert "スキップ" in result.stdout
            assert "未対応のタイプ" in result.stdout
            assert "0件作成, 1件スキップ" in result.stdout
        finally:
            Path(temp_path).unlink()

    def test_create_recipe_success(self):
        """Recipeタイプのページが正常に作成されること"""
        self.mock_sandpiper_app.create_recipe.execute.return_value = InsertedRecipe(
            id="recipe-page-id",
            title="きな粉蒸しパン",
        )

        recipe_data = [
            {
                "type": "Recipe",
                "title": "きな粉蒸しパン",
                "reference_url": "https://example.com",
                "ingredients": [
                    {"name": "絹豆腐", "quantity": "150g"},
                    {"name": "きな粉", "quantity": "50g"},
                ],
                "steps": ["混ぜる", "加熱する"],
            }
        ]

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(recipe_data, f, ensure_ascii=False)
            temp_path = f.name

        try:
            result = self.runner.invoke(self.app, ["create-notion-pages", temp_path])
            assert result.exit_code == 0
            assert "作成完了" in result.stdout
            assert "きな粉蒸しパン" in result.stdout
            assert "1件作成, 0件スキップ" in result.stdout

            # create_recipeが正しい引数で呼ばれたことを確認
            self.mock_sandpiper_app.create_recipe.execute.assert_called_once()
            call_args = self.mock_sandpiper_app.create_recipe.execute.call_args[0][0]
            assert call_args.title == "きな粉蒸しパン"
            assert call_args.reference_url == "https://example.com"
            assert len(call_args.ingredients) == 2
            assert len(call_args.steps) == 2
        finally:
            Path(temp_path).unlink()

    def test_create_recipe_case_insensitive_type(self):
        """typeは大文字小文字を区別しないこと"""
        self.mock_sandpiper_app.create_recipe.execute.return_value = InsertedRecipe(
            id="recipe-page-id",
            title="Test Recipe",
        )

        recipe_data = [{"type": "recipe", "title": "Test Recipe", "ingredients": [], "steps": []}]

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(recipe_data, f)
            temp_path = f.name

        try:
            result = self.runner.invoke(self.app, ["create-notion-pages", temp_path])
            assert result.exit_code == 0
            assert "作成完了" in result.stdout
            self.mock_sandpiper_app.create_recipe.execute.assert_called_once()
        finally:
            Path(temp_path).unlink()

    def test_create_multiple_recipes(self):
        """複数のレシピを一度に作成できること"""
        self.mock_sandpiper_app.create_recipe.execute.side_effect = [
            InsertedRecipe(id="id-1", title="Recipe 1"),
            InsertedRecipe(id="id-2", title="Recipe 2"),
        ]

        recipe_data = [
            {"type": "Recipe", "title": "Recipe 1", "ingredients": [], "steps": []},
            {"type": "Recipe", "title": "Recipe 2", "ingredients": [], "steps": []},
        ]

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(recipe_data, f)
            temp_path = f.name

        try:
            result = self.runner.invoke(self.app, ["create-notion-pages", temp_path])
            assert result.exit_code == 0
            assert "2件作成, 0件スキップ" in result.stdout
            assert self.mock_sandpiper_app.create_recipe.execute.call_count == 2
        finally:
            Path(temp_path).unlink()

    def test_create_recipe_without_reference_url(self):
        """reference_urlなしでもレシピ作成できること"""
        self.mock_sandpiper_app.create_recipe.execute.return_value = InsertedRecipe(
            id="recipe-page-id",
            title="Simple Recipe",
        )

        recipe_data = [{"type": "Recipe", "title": "Simple Recipe", "ingredients": [], "steps": ["Do something"]}]

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(recipe_data, f)
            temp_path = f.name

        try:
            result = self.runner.invoke(self.app, ["create-notion-pages", temp_path])
            assert result.exit_code == 0
            assert "作成完了" in result.stdout

            call_args = self.mock_sandpiper_app.create_recipe.execute.call_args[0][0]
            assert call_args.reference_url is None
        finally:
            Path(temp_path).unlink()

    def test_mixed_types(self):
        """異なるタイプが混在する場合、Recipeのみ処理されること"""
        self.mock_sandpiper_app.create_recipe.execute.return_value = InsertedRecipe(
            id="recipe-page-id",
            title="Test Recipe",
        )

        mixed_data = [
            {"type": "Recipe", "title": "Test Recipe", "ingredients": [], "steps": []},
            {"type": "Note", "title": "Test Note"},
            {"type": "Task", "title": "Test Task"},
        ]

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(mixed_data, f)
            temp_path = f.name

        try:
            result = self.runner.invoke(self.app, ["create-notion-pages", temp_path])
            assert result.exit_code == 0
            assert "1件作成, 2件スキップ" in result.stdout
            self.mock_sandpiper_app.create_recipe.execute.assert_called_once()
        finally:
            Path(temp_path).unlink()

    def test_recipe_creation_error_handling(self):
        """レシピ作成でエラーが発生した場合もエラーメッセージが表示されること"""
        self.mock_sandpiper_app.create_recipe.execute.side_effect = Exception("API Error")

        recipe_data = [{"type": "Recipe", "title": "Error Recipe", "ingredients": [], "steps": []}]

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(recipe_data, f)
            temp_path = f.name

        try:
            result = self.runner.invoke(self.app, ["create-notion-pages", temp_path])
            # エラーが発生しても他のアイテムの処理は続行される
            assert "エラー" in result.stdout
            assert "Error Recipe" in result.stdout
            assert "API Error" in result.stdout
        finally:
            Path(temp_path).unlink()

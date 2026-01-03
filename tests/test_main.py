"""main.pyのテスト"""

from unittest.mock import Mock, patch

from typer.testing import CliRunner

from sandpiper import __version__
from sandpiper.main import app


class TestCLI:
    """CLIアプリケーションのテスト"""

    def setup_method(self) -> None:
        """テスト用のCLIランナーをセットアップ"""
        self.runner = CliRunner()

    def test_hello_default(self) -> None:
        """デフォルトの挨拶をテスト"""
        result = self.runner.invoke(app, ["hello"])
        assert result.exit_code == 0
        assert "こんにちは、World!" in result.stdout

    def test_hello_with_name(self) -> None:
        """名前を指定した挨拶をテスト"""
        result = self.runner.invoke(app, ["hello", "--name", "テスト"])
        assert result.exit_code == 0
        assert "こんにちは、テスト!" in result.stdout

    def test_version(self) -> None:
        """バージョン表示をテスト"""
        result = self.runner.invoke(app, ["version"])
        assert result.exit_code == 0
        assert __version__ in result.stdout

    @patch('sandpiper.main.sandpiper_app.create_todo.execute')
    def test_create_todo_basic(self, mock_execute) -> None:
        """基本的なToDo作成をテスト"""
        result = self.runner.invoke(app, ["create-todo", "テストタスク"])
        assert result.exit_code == 0
        mock_execute.assert_called_once()

        # 呼び出し引数を確認
        call_args = mock_execute.call_args
        assert call_args[1]["request"].title == "テストタスク"
        assert call_args[1]["enableStart"] is False

    @patch('sandpiper.main.sandpiper_app.create_todo.execute')
    def test_create_todo_with_start(self, mock_execute) -> None:
        """開始フラグ付きToDo作成をテスト"""
        result = self.runner.invoke(app, ["create-todo", "開始タスク", "--start"])
        assert result.exit_code == 0
        mock_execute.assert_called_once()

        # 呼び出し引数を確認
        call_args = mock_execute.call_args
        assert call_args[1]["request"].title == "開始タスク"
        assert call_args[1]["enableStart"] is True

    @patch('sandpiper.main.sandpiper_app.create_repeat_project_task.execute')
    def test_create_repeat_project_tasks_default(self, mock_execute) -> None:
        """デフォルトの繰り返しプロジェクトタスク作成をテスト"""
        result = self.runner.invoke(app, ["create-repeat-project-tasks"])
        assert result.exit_code == 0
        mock_execute.assert_called_once_with(is_tomorrow=False)

    @patch('sandpiper.main.sandpiper_app.create_repeat_project_task.execute')
    def test_create_repeat_project_tasks_tomorrow(self, mock_execute) -> None:
        """明日用の繰り返しプロジェクトタスク作成をテスト"""
        result = self.runner.invoke(app, ["create-repeat-project-tasks", "--tomorrow"])
        assert result.exit_code == 0
        mock_execute.assert_called_once_with(is_tomorrow=True)

    @patch('sandpiper.main.sandpiper_app.get_todo_log.execute')
    def test_get_todo_log_default(self, mock_execute) -> None:
        """デフォルトのToDOログ取得をテスト"""
        # モックのToDOデータを設定
        mock_todo = Mock()
        mock_todo.title = "テストタスク"
        mock_todo.kind.value = "単発"
        mock_todo.project_name = "テストプロジェクト"
        mock_todo.perform_range = (
            Mock(**{'strftime.return_value': '2024-01-15 10:00'}),
            Mock(**{'strftime.return_value': '2024-01-15 11:00'})
        )
        mock_execute.return_value = [mock_todo]

        result = self.runner.invoke(app, ["get-todo-log"])
        assert result.exit_code == 0
        assert "テストタスク" in result.stdout
        mock_execute.assert_called_once()

    @patch('sandpiper.main.sandpiper_app.get_todo_log.execute')
    def test_get_todo_log_json(self, mock_execute) -> None:
        """JSON形式でのToDOログ取得をテスト"""
        # モックのToDOデータを設定
        mock_todo = Mock()
        mock_todo.title = "JSONタスク"
        mock_todo.kind.value = "プロジェクト"
        mock_todo.project_name = "JSONプロジェクト"
        mock_todo.perform_range = (
            Mock(**{'strftime.return_value': '2024-01-15 09:00'}),
            Mock(**{'strftime.return_value': '2024-01-15 10:00'})
        )
        mock_execute.return_value = [mock_todo]

        result = self.runner.invoke(app, ["get-todo-log", "--json"])
        assert result.exit_code == 0
        assert "JSONタスク" in result.stdout
        assert "JSONプロジェクト" in result.stdout
        mock_execute.assert_called_once()

    @patch('sandpiper.main.sandpiper_app.get_todo_log.execute')
    def test_get_todo_log_markdown(self, mock_execute) -> None:
        """Markdown形式でのToDOログ取得をテスト"""
        # モックのToDOデータを設定
        mock_todo = Mock()
        mock_todo.title = "Markdownタスク"
        mock_todo.kind.value = "リピート"
        mock_todo.project_name = "Markdownプロジェクト"
        mock_todo.perform_range = (
            Mock(**{'strftime.return_value': '2024-01-15 08:00'}),
            Mock(**{'strftime.return_value': '2024-01-15 09:00'})
        )
        mock_execute.return_value = [mock_todo]

        result = self.runner.invoke(app, ["get-todo-log", "--markdown"])
        assert result.exit_code == 0
        assert "| タイトル | 種別 | プロジェクト | 実施期間 |" in result.stdout
        assert "Markdownタスク" in result.stdout
        mock_execute.assert_called_once()

    @patch('sandpiper.main.sandpiper_app.get_todo_log.execute')
    def test_get_todo_log_without_perform_range(self, mock_execute) -> None:
        """実施期間なしのToDOログ取得をテスト"""
        # perform_rangeがないモックのToDOデータを設定
        mock_todo = Mock()
        mock_todo.title = "期間なしタスク"
        mock_todo.kind.value = "差し込み"
        mock_todo.project_name = ""
        # perform_rangeがないことをシミュレート
        del mock_todo.perform_range
        mock_execute.return_value = [mock_todo]

        result = self.runner.invoke(app, ["get-todo-log", "--json"])
        assert result.exit_code == 0
        assert "期間なしタスク" in result.stdout
        mock_execute.assert_called_once()

    @patch('sandpiper.main.sandpiper_app.get_todo_log.execute')
    def test_get_todo_log_markdown_without_perform_range(self, mock_execute) -> None:
        """perform_rangeがない場合のMarkdown出力をテスト（95行目のelse部分）"""
        # perform_rangeがないToDoオブジェクトをモック
        mock_todo = Mock()
        mock_todo.title = "期間なしタスク"
        mock_todo.kind = Mock()
        mock_todo.kind.value = "NORMAL"
        mock_todo.project_name = "テストプロジェクト"
        # perform_rangeが存在しない（None）状態をシミュレート
        mock_todo.perform_range = None
        mock_execute.return_value = [mock_todo]

        result = self.runner.invoke(app, ["get-todo-log", "--markdown"])
        assert result.exit_code == 0
        # 期間が空文字列になることを確認（95行目のelse部分）
        assert "| 期間なしタスク | NORMAL | テストプロジェクト |  |" in result.stdout
        mock_execute.assert_called_once()

    @patch('sandpiper.main.sandpiper_app.create_repeat_task.execute')
    def test_create_repeat_tasks_valid_date(self, mock_execute) -> None:
        """有効な日付での繰り返しタスク作成をテスト"""
        result = self.runner.invoke(app, ["create-repeat-tasks", "--basis-date", "2024-01-15"])
        assert result.exit_code == 0
        mock_execute.assert_called_once()

        # 呼び出し引数の日付を確認
        from datetime import date
        call_args = mock_execute.call_args
        assert call_args[1]["basis_date"] == date(2024, 1, 15)

    def test_create_repeat_tasks_invalid_date(self) -> None:
        """無効な日付での繰り返しタスク作成をテスト"""
        result = self.runner.invoke(app, ["create-repeat-tasks", "--basis-date", "invalid-date"])
        assert result.exit_code == 1
        assert "エラー: 日付の形式が正しくありません" in result.stdout

    def test_create_repeat_tasks_missing_date(self) -> None:
        """日付未指定での繰り返しタスク作成をテスト"""
        result = self.runner.invoke(app, ["create-repeat-tasks"])
        assert result.exit_code != 0  # 必須引数なのでエラー

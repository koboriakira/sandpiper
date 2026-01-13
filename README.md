# Sandpiper

個人のタスク管理を支援するPythonアプリケーション - Notion統合によるタスク管理、Slack通知、繰り返しタスクの自動生成

## 主な機能

- **タスク管理**: ToDo作成・開始・完了のライフサイクル管理
- **Notion統合**: NotionデータベースとのリアルタイムWebhook連携
- **繰り返しタスク**: 複雑な周期ルールに基づく自動タスク生成
- **GitHub活動ログ**: GitHub活動の可視化と日報機能
- **JIRA統合**: JIRAチケット検索・Notionプロジェクトへの同期
- **レシピ管理**: レシピ・買い物リストの管理
- **Webクリップ**: URL保存と自動タイトル取得
- **CLI/API**: typerによるCLI + FastAPIによるWebhook受信

## 必要要件

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) (推奨)

## セットアップ

```bash
# uvのインストール(まだの場合)
curl -LsSf https://astral.sh/uv/install.sh | sh

# プロジェクトのセットアップ
uv sync

# 環境変数の設定(.env.templateを参考に.envを作成)
cp .env.template .env
# .envを編集してAPI トークンを設定
```

## 開発コマンド

```bash
# テスト実行
uv run pytest

# テスト(カバレッジ付き)
uv run pytest --cov

# コードフォーマット
uv run ruff format .

# リンティング
uv run ruff check .

# 型チェック
uv run mypy

# アプリケーション実行
uv run sandpiper --help
uv run sandpiper hello --name "開発者"
```

## CLIコマンド

```bash
# タスク管理
uv run sandpiper create-todo "新しいタスク" --start
uv run sandpiper create-someday "いつかやるタスク"
uv run sandpiper get-todo-log --date 2024-03-20 --json
uv run sandpiper create-repeat-tasks --basis-date 2024-03-20

# プロジェクト管理
uv run sandpiper create-project "プロジェクト名" --start-date 2024-03-20
uv run sandpiper create-project-task "タスク名" --project-id "notion-page-id"

# GitHub活動ログ
uv run sandpiper get-github-activity --date 2024-03-20

# JIRA統合
uv run sandpiper search-jira-tickets --project "PROJ" --status "Open"
uv run sandpiper sync-jira-to-project --project "SU"
```

## Web API

```bash
# 開発サーバー起動
ENVIRONMENT=development uv run uvicorn sandpiper.api:app --reload

# APIドキュメント確認(開発時のみ)
# http://localhost:8000/docs

# レシピ登録フォーム(htmx)
# http://localhost:8000/api/recipe/new
```

### エンドポイント一覧
- `GET /api/recipe/new` - レシピ登録フォーム(htmx)
- `POST /api/recipe` - レシピ作成API
- `POST /api/notion/todo/start` - タスク開始
- `POST /api/notion/todo/complete` - タスク完了
- `POST /api/notion/clips` - Webクリップ作成

## 設定ファイル

すべての設定は `pyproject.toml` に統一されています：

- **ruff**: リンティングとフォーマット
- **pytest**: テストの実行と設定
- **mypy**: 型チェック
- **coverage**: カバレッジ測定

## CI/CD

GitHub Actionsによる自動化：

- マルチプラットフォーム(Linux、Windows、macOS)
- 複数Python バージョン(3.12、3.13)
- テスト、リンティング、型チェック
- release-pleaseによる自動リリース管理

## ライセンス

MIT License

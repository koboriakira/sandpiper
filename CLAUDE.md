# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## プロジェクト概要

Sandpiperは個人のタスク管理を支援するPythonアプリケーションです。Notion統合によるタスク管理、Slack通知、繰り返しタスクの自動生成などの機能を提供します。

### 主な機能
- **タスク管理**: ToDo作成・開始・完了のライフサイクル管理
- **Notion統合**: NotionデータベースとのリアルタイムWebhook連携
- **Slack通知**: タスク完了時の自動Slack通知
- **繰り返しタスク**: 複雑な周期ルールに基づく自動タスク生成
- **GitHub活動ログ**: PyGithubによるGitHub活動の可視化と日報機能
- **JIRA統合**: JIRAチケットの検索・取得とNotionプロジェクトへの同期
- **レシピ管理**: Notionデータベースでのレシピ・買い物リスト管理
- **Clips管理**: Webクリップの保存・自動タイトル取得
- **サムデイリスト**: いつかやるタスクの管理
- **CLI**: typerによる使いやすいコマンドラインインターフェース
- **Web API**: FastAPIによるNotion Webhook受信とヘルスチェック

### アーキテクチャ特徴
- **ドメイン駆動設計**: plan/perform/review/calendar/recipe/clipsドメインによる責務分離
- **イベントドリブン**: EventBusによる疎結合なコンポーネント設計
- **CQRS**: コマンド(変更)とクエリ(参照)の分離
- **Notion中心**: Notionデータベースをメインデータストアとした統合設計

## 開発環境とツール

### パッケージ管理: uv
- **uv**: 超高速なRust製パッケージマネージャー(pip、venv、pipxの代替)
- 仮想環境の自動管理とキャッシュ最適化により10-100倍高速

### 必須開発コマンド

```bash
# 環境セットアップ
uv sync                          # 依存関係をインストール(初回・更新時)

# CLI実行
uv run sandpiper hello --name "開発者"          # 挨拶コマンド
uv run sandpiper create-todo "新しいタスク" --start # タスク作成・開始
uv run sandpiper create-someday "いつかやるタスク"  # サムデイリストに追加
uv run sandpiper get-todo-log --date 2024-03-20 --json  # 完了タスクログ(JSON)
uv run sandpiper get-todo-log --date 2024-03-20 --markdown  # 完了タスクログ(Markdown)
uv run sandpiper get-github-activity            # GitHub活動ログ取得(今日)
uv run sandpiper get-github-activity --date 2024-03-20 --json  # 特定日・JSON形式
uv run sandpiper create-repeat-tasks --basis-date 2024-03-20  # 繰り返しタスク作成
uv run sandpiper create-repeat-project-tasks --tomorrow       # 明日のプロジェクトタスク作成

# プロジェクト管理
uv run sandpiper create-project "プロジェクト名" --start-date 2024-03-20
uv run sandpiper create-project-task "タスク名" --project-id "notion-page-id"

# JIRA統合
uv run sandpiper search-jira-tickets --project "PROJ" --status "Open" # JIRAチケット検索
uv run sandpiper search-jira-tickets --assignee "currentUser()" --max-results 10 # 自分に割り当てられたチケット
uv run sandpiper search-jira-tickets --jql "project = PROJ AND status != Done" # JQLでの検索
uv run sandpiper get-jira-ticket "PROJ-123"     # 個別チケットの詳細取得
uv run sandpiper sync-jira-to-project --project "SU"  # JIRAチケットをNotionプロジェクトに同期

# テスト実行
uv run pytest                    # 基本テスト実行
uv run pytest --cov             # カバレッジ付きテスト
uv run pytest -v                # 詳細モード
uv run pytest tests/test_*.py   # 特定のテストファイル

# FastAPI開発サーバー起動
# 開発モード(セキュリティ制限緩和、APIドキュメント有効)
ENVIRONMENT=development uv run uvicorn sandpiper.api:app --reload

# コード品質チェック
uv run ruff check .              # リンティング
uv run ruff format .             # フォーマット
uv run mypy                      # 型チェック

# 統合品質チェック(Claude Code hooks)
.claude/scripts/pre-commit-replacement.sh  # 統合品質チェック
```

### パッケージ操作
```bash
uv add package-name              # 本番依存関係追加
uv add --group dev package-name  # 開発依存関係追加
uv remove package-name           # パッケージ削除
```

## アーキテクチャ・プロジェクト構造

### ドメイン駆動設計(DDD)によるマルチドメインアーキテクチャ

```
src/sandpiper/
├── plan/                        # タスク計画・作成ドメイン
│   ├── domain/                  # ドメインモデル(Todo, Routine, Project, SomedayItem)
│   ├── application/             # ユースケース(CreateTodo, CreateRepeatTask, SyncJiraToProject)
│   ├── infrastructure/          # Notionリポジトリ実装
│   └── query/                   # 読み取り専用クエリ(CQRS) + JIRA統合
├── perform/                     # タスク実行ドメイン
│   ├── domain/                  # 実行状態管理(Todo開始・完了)
│   ├── application/             # 実行ユースケース(StartTodo, CompleteTodo)
│   └── infrastructure/          # Notion実行状態リポジトリ
├── review/                      # タスクレビュー・分析ドメイン
│   ├── application/             # 分析ユースケース(GetTodoLog, GetGitHubActivity)
│   └── query/                   # 実行結果クエリ(TodoQuery, GitHubActivityQuery, CalendarQuery)
├── calendar/                    # カレンダー管理ドメイン
│   ├── domain/                  # カレンダーイベントモデル
│   ├── application/             # イベント作成・削除ユースケース
│   └── infrastructure/          # Notionカレンダーリポジトリ
├── recipe/                      # レシピ管理ドメイン
│   ├── domain/                  # レシピ・買い物リストモデル
│   ├── application/             # レシピ作成ユースケース
│   └── infrastructure/          # Notionレシピリポジトリ
├── clips/                       # Webクリップ管理ドメイン
│   ├── domain/                  # クリップモデル
│   ├── application/             # クリップ作成ユースケース
│   └── infrastructure/          # Notionクリップリポジトリ
├── shared/                      # 共通コンポーネント
│   ├── event/                   # ドメインイベント(TodoStarted, TodoCompleted, TodoCreated)
│   ├── infrastructure/          # EventBus, Slack通知, GitHubClient, Commentator
│   ├── notion/                  # Notion API統合(lotion + notion-client)
│   │   └── databases/           # 各Notionデータベース設定
│   ├── utils/                   # 日付ユーティリティ
│   └── valueobject/             # 値オブジェクト(TaskChuteSection, Context)
├── app/                         # アプリケーション統合
│   ├── app.py                   # DI設定とbootstrap(SandPiperApp)
│   ├── message_dispatcher.py    # メッセージ配信
│   └── handlers/                # 特殊タスクハンドラー
├── routers/                     # FastAPIエンドポイント
│   ├── notion.py                # Notion Webhook受信
│   ├── recipe.py                # レシピ管理API(htmxフロントエンド含む)
│   ├── health.py                # ヘルスチェック
│   ├── maintenance.py           # メンテナンスAPI
│   └── dependency/              # 認証・依存性注入
├── templates/                   # Jinja2テンプレート(htmx)
│   ├── base.html                # 共通レイアウト
│   └── recipe_form.html         # レシピ登録フォーム
├── main.py                      # CLIエントリーポイント(typer)
└── api.py                       # FastAPIエントリーポイント
```

### 主要コンポーネント

#### ドメインモデル
- **Todo**: タスクエンティティ(status: TODO/IN_PROGRESS/DONE)
- **Routine**: 繰り返しルール(毎日、毎週、月次、特定曜日)
- **Project**: プロジェクトエンティティ(JIRA連携対応)
- **ProjectTask**: プロジェクトタスク
- **SomedayItem**: いつかやるタスク(タイミング属性付き)
- **CalendarEvent**: カレンダーイベント
- **Recipe**: レシピ(材料・手順)
- **Clip**: Webクリップ(自動タイトル取得対応)
- **EventBus**: 軽量イベント配信システム

#### 外部サービス統合
- **Notion API**: lotion(日本製)+ notion-client(公式SDK)
- **Slack API**: slack-sdk(タスク完了通知)
- **GitHub API**: PyGithub(活動ログ取得)
- **JIRA API**: requests + JIRA REST API v3(チケット管理・検索・Notion同期)
- **Webhook**: Notion → FastAPI リアルタイム連携

#### データベース構成(Notion)
- **ROUTINE**: 繰り返しルール管理
- **TODO**: タスク管理
- **PROJECT_TASK**: プロジェクトタスク管理
- **PROJECT**: プロジェクト管理
- **CALENDAR**: カレンダーイベント
- **RECIPE**: レシピ管理
- **SHOPPING**: 買い物リスト
- **CLIPS**: Webクリップ
- **SOMEDAY**: いつかやるリスト
- **INBOX**: インボックス

## 開発ワークフロー

### 環境変数設定

#### 必須環境変数(Notion・Slack・GitHub・JIRA統合)
```bash
# Notion API設定
export NOTION_SECRET="secret_****"           # Notion Integration Token

# Slack通知設定
export SLACK_BOT_TOKEN="xoxb-****"         # Slack Bot Token

# GitHub API設定
export GITHUB_TOKEN="ghp_****"             # GitHub Personal Access Token

# JIRA API設定
export BUSINESS_JIRA_USERNAME="user@company.com"    # JIRA ユーザー名(メールアドレス)
export BUSINESS_JIRA_API_TOKEN="ATATT****"          # JIRA API トークン
export BUSINESS_JIRA_BASE_URL="https://company.atlassian.net"  # JIRA Base URL (オプション)

# FastAPI設定
export ENVIRONMENT=development              # 開発環境設定
```

### 新機能開発
1. テスト作成: `tests/test_*.py`
2. 実装: `src/sandpiper/`
3. テスト実行: `uv run pytest`
4. コード品質: `uv run ruff check . && uv run ruff format .`
5. 型チェック: `uv run mypy`

### テスト駆動開発サイクル
```bash
# 1. テスト作成・実行(失敗確認)
uv run pytest tests/test_new_feature.py -v

# 2. 実装
# コードを書く

# 3. テスト実行(成功確認)
uv run pytest tests/test_new_feature.py -v

# 4. 品質チェック
uv run ruff check . && uv run ruff format . && uv run mypy
```

## コーディング規約

### インポート順序
1. 標準ライブラリ
2. サードパーティライブラリ
3. ローカルモジュール(`from . import`、`from sandpiper import`)

### 型ヒント
- Python 3.12+ の現代的な型ヒント使用
- `from typing import`より組み込み型を優先(`list[str]`、`dict[str, Any]`)
- 関数の引数と戻り値に型ヒント必須

### テスト
- `pytest`使用、classベーステスト推奨
- 各テストメソッドは`test_*`命名
- `@pytest.mark.parametrize`でデータ駆動テスト活用
- カバレッジ80%以上維持

## CI/CDとツール連携

### GitHub Actions
- マルチプラットフォーム(Linux、Windows、macOS)
- Python 3.12、3.13 サポート
- テスト・リンティング・型チェック・セキュリティ監査

### Release Please(自動リリース管理)
- **Conventional Commits**に基づく自動バージョニング
- CHANGELOG.md自動生成・更新
- GitHub Releases自動作成

#### Conventional Commits形式
```bash
# パッチバージョン更新 (0.1.0 → 0.1.1)
git commit -m "fix: バリデーションエラーを修正"

# マイナーバージョン更新 (0.1.0 → 0.2.0)
git commit -m "feat: 新しいCLIコマンド追加"

# メジャーバージョン更新 (0.1.0 → 1.0.0)
git commit -m "feat!: APIの破壊的変更"

# リリースに含まれないコミット
git commit -m "docs: README更新"
git commit -m "chore: 依存関係更新"
```

## ドメイン固有の開発ガイドライン

### 新しいドメイン追加パターン
```python
# 1. domain/ - ドメインモデルとリポジトリインターフェース
# 2. application/ - ユースケース実装
# 3. infrastructure/ - Notionリポジトリ実装
# 4. query/ - CQRSクエリ(必要に応じて)

# 5. app/app.py で DI設定とSandPiperAppへの登録
# 6. main.py でCLIコマンド追加
# 7. routers/ でWebAPI追加(必要に応じて)
```

### イベントドリブン開発
```python
# 1. イベント定義(shared/event/)
class NewDomainEvent:
    def __init__(self, data: str):
        self.data = data

# 2. イベントハンドラー作成
def handle_new_event(event: NewDomainEvent):
    pass

# 3. bootstrap()でハンドラー登録
event_bus.subscribe(NewDomainEvent, handle_new_event)
```

## 注意事項

- uvコマンドは必ず`uv run`プレフィックス使用(仮想環境自動活用)
- pyproject.toml直接編集せず`uv add`/`uv remove`使用
- テストは必ず`tests/`ディレクトリに配置、`test_*.py`命名

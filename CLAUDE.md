# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## プロジェクト概要

Sandpiperは個人のタスク管理を支援するPythonアプリケーションです。Notion統合によるタスク管理、Slack通知、繰り返しタスクの自動生成などの機能を提供します。

### 主な機能
- **タスク管理**: ToDo作成・開始・完了のライフサイクル管理
- **Notion統合**: NotionデータベースとのリアルタイムWebhook連携
- **Slack通知**: タスク完了時の自動Slack通知
- **繰り返しタスク**: 複雑な周期ルールに基づく自動タスク生成
- **CLI**: typerによる使いやすいコマンドラインインターフェース
- **Web API**: FastAPIによるNotion Webhook受信とヘルスチェック

### アーキテクチャ特徴
- **ドメイン駆動設計**: plan/perform/reviewドメインによる責務分離
- **イベントドリブン**: EventBusによる疎結合なコンポーネント設計
- **CQRS**: コマンド（変更）とクエリ（参照）の分離
- **Notion中心**: Notionデータベースをメインデータストアとした統合設計

## 開発環境とツール

### パッケージ管理: uv
- **uv**: 超高速なRust製パッケージマネージャー（pip、venv、pipxの代替）
- 仮想環境の自動管理とキャッシュ最適化により10-100倍高速

### 必須開発コマンド

```bash
# 環境セットアップ
uv sync                          # 依存関係をインストール（初回・更新時）

# CLI実行
uv run sandpiper hello --name "開発者"          # 挨拶コマンド
uv run sandpiper create-todo "新しいタスク" --start # タスク作成・開始
uv run sandpiper get-todo-log --json            # 完了タスクログ（JSON）
uv run sandpiper get-todo-log --markdown        # 完了タスクログ（Markdown）
uv run sandpiper create-repeat-tasks --basis-date 2024-03-20  # 繰り返しタスク作成
uv run sandpiper create-repeat-project-tasks --tomorrow       # 明日のプロジェクトタスク作成

# テスト実行
uv run pytest                    # 基本テスト実行
uv run pytest --cov             # カバレッジ付きテスト
uv run pytest -v                # 詳細モード
uv run pytest tests/test_*.py   # 特定のテストファイル

# FastAPI開発サーバー起動
# 開発モード（セキュリティ制限緩和、APIドキュメント有効）
ENVIRONMENT=development uv run uvicorn sandpiper.api:app --reload

# 本番モード（Notion Webhook受信用）
ENVIRONMENT=production ALLOWED_ORIGINS=https://notion.so uv run uvicorn sandpiper.api:app --host 0.0.0.0

# コード品質チェック
uv run ruff check .              # リンティング
uv run ruff format .             # フォーマット
uv run mypy                      # 型チェック

# 統合品質チェック（Claude Code hooks）
.claude/scripts/pre-commit-replacement.sh  # 統合品質チェック
.claude/scripts/code-quality.sh           # Python コード品質チェック
.claude/scripts/run-tests.sh              # テスト実行
.claude/scripts/file-checks.sh            # ファイル品質チェック
```

### パッケージ操作
```bash
uv add package-name              # 本番依存関係追加
uv add --group dev package-name  # 開発依存関係追加
uv remove package-name           # パッケージ削除
```

## アーキテクチャ・プロジェクト構造

### ドメイン駆動設計（DDD）による3層アーキテクチャ

```
src/sandpiper/
├── plan/                        # タスク計画・作成ドメイン
│   ├── domain/                  # ドメインモデル（Todo, Routine, ProjectTaskRule）
│   ├── application/             # ユースケース（CreateTodo, CreateRepeatTask）
│   ├── infrastructure/          # Notionリポジトリ実装
│   └── query/                   # 読み取り専用クエリ（CQRS）
├── perform/                     # タスク実行ドメイン
│   ├── domain/                  # 実行状態管理（Todo開始・完了）
│   ├── application/             # 実行ユースケース（StartTodo, CompleteTodo）
│   └── infrastructure/          # Notion実行状態リポジトリ
├── review/                      # タスクレビュー・分析ドメイン
│   ├── application/             # 分析ユースケース（GetTodoLog）
│   └── query/                   # 実行結果クエリ
├── shared/                      # 共通コンポーネント
│   ├── event/                   # ドメインイベント（TodoStarted, TodoCompleted）
│   ├── infrastructure/          # EventBus, Slack通知, Notionコメント
│   ├── notion/                  # Notion API統合（lotion + notion-client）
│   ├── utils/                   # 日付ユーティリティ
│   └── valueobject/             # 値オブジェクト（TaskChuteSection）
├── app/                         # アプリケーション統合
│   ├── app.py                   # DI設定とbootstrap
│   └── message_dispatcher.py    # メッセージ配信
├── routers/                     # FastAPIエンドポイント
│   ├── notion.py                # Notion Webhook受信
│   ├── health.py                # ヘルスチェック
│   └── dependency/              # 認証・依存性注入
├── main.py                      # CLIエントリーポイント（typer）
└── api.py                       # FastAPIエントリーポイント
```

### 主要コンポーネント

#### ドメインモデル
- **Todo**: タスクエンティティ（status: TODO/IN_PROGRESS/DONE）
- **Routine**: 繰り返しルール（毎日、毎週、月次、特定曜日）
- **ProjectTaskRule**: プロジェクトタスクルール
- **EventBus**: 軽量イベント配信システム

#### 外部サービス統合
- **Notion API**: lotion（日本製）+ notion-client（公式SDK）
- **Slack API**: slack-sdk（タスク完了通知）
- **Webhook**: Notion → FastAPI リアルタイム連携

#### データベース構成
- **ROUTINE**: 繰り返しルール管理
- **TODO**: タスク管理
- **PROJECT_TASK**: プロジェクトタスク管理
- **PROJECT**: プロジェクト管理

## 設定ファイルの重要性

**pyproject.toml**: 全ツール設定の中心
- プロジェクトメタデータ、依存関係
- ruff（リンター/フォーマッター）設定
- pytest、mypy、coverage設定
- 依存関係グループ（dev、test、docs）

## 開発ワークフロー

### 環境変数設定

#### 必須環境変数（Notion・Slack統合）
```bash
# Notion API設定
export NOTION_TOKEN="secret_****"           # Notion Integration Token
export SLACK_BOT_TOKEN="xoxb-****"         # Slack Bot Token

# FastAPI設定
export ENVIRONMENT=development              # 開発環境設定
export DEBUG=true                          # デバッグモード
export ALLOWED_ORIGINS=https://notion.so   # 本番時のCORS設定
```

#### 開発フロー

**CLIアプリケーション開発:**
```bash
# 1. 新しいCLIコマンド追加
# main.py に @app.command() 関数を追加
# app/app.py でサービス初期化

# 2. テスト実行
uv run pytest tests/test_main.py -v

# 3. 動作確認
uv run sandpiper your-new-command --help
```

**WebAPIアプリケーション開発（Webhook受信）:**
```bash
# 1. API開発サーバー起動
ENVIRONMENT=development uv run uvicorn sandpiper.api:app --reload

# 2. Webhookテスト（ローカル）
# ngrok等でローカルサーバーを公開
# NotionでWebhook URLを設定

# 3. エンドポイント確認
# http://localhost:8000/docs (開発時のみ)
# GET /api/version (ヘルスチェック)
# POST /api/notion/todo/start (Webhook受信)
```

### 新機能開発
1. テスト作成: `tests/test_*.py`
2. 実装: `src/sandpiper/`
3. テスト実行: `uv run pytest`
4. コード品質: `uv run ruff check . && uv run ruff format .`
5. 型チェック: `uv run mypy`

### テスト駆動開発サイクル
```bash
# 1. テスト作成・実行（失敗確認）
uv run pytest tests/test_new_feature.py -v

# 2. 実装
# コードを書く

# 3. テスト実行（成功確認）
uv run pytest tests/test_new_feature.py -v

# 4. 品質チェック
uv run ruff check . && uv run ruff format . && uv run mypy
```

## コーディング規約

### インポート順序
1. 標準ライブラリ
2. サードパーティライブラリ
3. ローカルモジュール（`from . import`、`from sandpiper import`）

### 型ヒント
- Python 3.12+ の現代的な型ヒント使用
- `from typing import`より組み込み型を優先（`list[str]`、`dict[str, Any]`）
- 関数の引数と戻り値に型ヒント必須

### テスト
- `pytest`使用、classベーステスト推奨
- 各テストメソッドは`test_*`命名
- `@pytest.mark.parametrize`でデータ駆動テスト活用
- カバレッジ80%以上維持

## CI/CDとツール連携

### GitHub Actions
- マルチプラットフォーム（Linux、Windows、macOS）
- Python 3.12、3.13 サポート
- テスト・リンティング・型チェック・セキュリティ監査

### Claude Code hooks（AI統合品質管理）
- **ファイル変更時**: 自動的にコード品質チェックを提案
- **コミット時**: リンティング、フォーマット、型チェック、テスト実行
- **設定ファイル**: `.claude/settings.local.json` で hooks 設定管理

#### 利用可能なhooksスクリプト
```bash
# 統合品質チェック（推奨）
.claude/scripts/pre-commit-replacement.sh

# 個別チェック
.claude/scripts/code-quality.sh     # ruff + mypy
.claude/scripts/run-tests.sh        # pytest実行
.claude/scripts/file-checks.sh      # ファイル品質
```

#### hooks自動実行タイミング
- **PostToolUse**: Write/Edit/MultiEdit 後にファイルチェック提案
- **UserPromptSubmit**: 「コミット」関連プロンプトで品質チェック実行

### 従来のpre-commit（手動開発時）
- **Git hooks統合**: コミット前の自動品質チェック
- **設定ファイル**: `.pre-commit-config.yaml`
- **手動実行**: `uv run pre-commit run --all-files`

#### 使い分けの指針
- **Claude Code使用時**: Claude Code hooks（AI統合、リアルタイム提案）
- **手動開発時**: 従来のpre-commit（Git hooks、コミット時実行）
- **CI/CD**: 両方の設定をGitHub Actionsで活用

### Release Please（自動リリース管理）
- **Conventional Commits**に基づく自動バージョニング
- CHANGELOG.md自動生成・更新
- GitHub Releases自動作成
- PyPI自動公開（本番・テスト環境）

#### リリース関連コマンド
```bash
# リリース手動トリガー（通常は自動実行）
gh workflow run release-please.yml

# リリース状態確認
gh release list

# 特定リリース詳細
gh release view v1.0.0
```

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
git commit -m "ci: CI設定改善"
```

## 依存関係管理

### 本番依存関係
- `pydantic`: データバリデーション
- `httpx`: 非同期HTTPクライアント
- `rich`: 美しいターミナル出力
- `typer`: CLIアプリケーション構築
- `fastapi`: モダンなWeb APIフレームワーク
- `uvicorn`: ASGI サーバー

### 開発依存関係
- `pytest`: テストフレームワーク + プラグイン
- `ruff`: 高速リンター・フォーマッター
- `mypy`: 静的型チェッカー
- `pre-commit`: Git フック管理

## ドメイン固有の開発ガイドライン

### タスク管理ドメインの理解

#### 1. planドメイン（タスク計画）
```python
# 新しいタスク作成
from sandpiper.plan.application.create_todo import CreateNewToDoRequest
request = CreateNewToDoRequest(title="新機能実装")
sandpiper_app.create_todo.execute(request, enableStart=True)

# 繰り返しタスクルール
from sandpiper.plan.domain.routine_cycle import RoutineCycle
cycle = RoutineCycle.create_weekly(["月", "水", "金"])  # 月水金の繰り返し
```

#### 2. performドメイン（タスク実行）
```python
# タスク開始・完了のイベント処理
from sandpiper.shared.event.todo_started import TodoStartedEvent
from sandpiper.shared.event.todo_completed import TodoCompletedEvent

# EventBusによる非同期処理
event_bus.publish(TodoCompletedEvent(todo_id="123"))
```

#### 3. reviewドメイン（振り返り）
```python
# 完了タスクの分析
result = sandpiper_app.get_todo_log.execute()
for todo in result:
    print(f"{todo.title} - {todo.project_name} - {todo.perform_range}")
```

### Notion統合開発

#### データベース設定
```python
# src/sandpiper/shared/notion/database_config.py
# 各データベースIDは実際のNotionデータベースIDに対応
ROUTINE_DATABASE_ID = "actual-notion-database-id"
TODO_DATABASE_ID = "actual-notion-database-id"
```

#### Webhookエンドポイント開発
```python
# routers/notion.py での新しいWebhook追加例
@router.post("/todo/update")
async def handle_todo_update(request: dict, app=Depends(get_app)):
    # Notionからの更新イベント処理
    pass
```

### イベントドリブン開発

#### 新しいドメインイベント追加
```python
# 1. イベント定義
class NewDomainEvent:
    def __init__(self, data: str):
        self.data = data

# 2. イベントハンドラー作成
def handle_new_event(event: NewDomainEvent):
    # イベント処理ロジック
    pass

# 3. bootstrap()でハンドラー登録
event_bus.subscribe(NewDomainEvent, handle_new_event)
```

## 注意事項

- uvコマンドは必ず`uv run`プレフィックス使用（仮想環境自動活用）
- pyproject.toml直接編集せず`uv add`/`uv remove`使用
- 新しい依存関係追加時は適切なグループ（dev/test/docs）に分類
- テストは必ず`tests/`ディレクトリに配置、`test_*.py`命名
- Claude Code機能により開発効率が大幅向上、積極的活用推奨

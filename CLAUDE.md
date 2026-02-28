# CLAUDE.md

## プロジェクト概要

Sandpiperは個人のタスク管理を支援するPythonアプリケーション。Notion統合、Slack通知、繰り返しタスク自動生成、JIRA連携、GitHub活動ログ、レシピ管理、Webクリップ管理などの機能を持つ。

### アーキテクチャ
- **DDD**: plan/perform/review/calendar/recipe/clipsドメインによる責務分離
- **イベントドリブン**: EventBusによる疎結合設計
- **CQRS**: コマンドとクエリの分離
- **Notion中心**: Notionデータベースをメインデータストアとして使用

## 開発コマンド

```bash
uv sync                          # 依存関係インストール
uv run sandpiper <command>       # CLI実行（--helpで全コマンド確認可能）
uv run pytest                    # テスト実行
uv run ruff check . && uv run ruff format .  # リント・フォーマット
uv run mypy                      # 型チェック
.claude/scripts/pre-commit-replacement.sh    # 統合品質チェック
ENVIRONMENT=development uv run uvicorn sandpiper.api:app --reload  # 開発サーバー
uv add <pkg> / uv add --group dev <pkg>      # パッケージ追加
```

## プロジェクト構造

```
src/sandpiper/
├── plan/          # タスク計画・作成（Todo, Routine, Project, Someday, JIRA同期）
├── perform/       # タスク実行（開始・完了）
├── review/        # レビュー・分析（TodoLog, GitHub活動, Calendar）
├── calendar/      # カレンダーイベント管理
├── recipe/        # レシピ・買い物リスト管理
├── clips/         # Webクリップ管理
├── shared/        # EventBus, Slack通知, Notion API統合, ユーティリティ
├── app/           # DI設定(app.py), メッセージ配信, ハンドラー
├── routers/       # FastAPIエンドポイント（Webhook, レシピ, ヘルスチェック）
├── main.py        # CLIエントリーポイント(typer)
└── api.py         # FastAPIエントリーポイント
```

各ドメインは `domain/` `application/` `infrastructure/` `query/` の標準DDD構造を持つ。

## 環境変数

必須: `NOTION_SECRET`, `SLACK_BOT_TOKEN`, `GITHUB_TOKEN`
JIRA統合: `BUSINESS_JIRA_USERNAME`, `BUSINESS_JIRA_API_TOKEN`, `BUSINESS_JIRA_BASE_URL`
FastAPI: `ENVIRONMENT=development`

## コーディング規約

- インポート順: 標準ライブラリ → サードパーティ → ローカル
- Python 3.12+ 型ヒント使用（組み込み型優先: `list[str]`, `dict[str, Any]`）
- テスト: pytest, classベース推奨, `@pytest.mark.parametrize` 活用, カバレッジ80%以上

## CI/CD

- GitHub Actions: Python 3.12/3.13, テスト・リント・型チェック・セキュリティ監査
- Release Please: Conventional Commits (`feat:`, `fix:`) に基づく自動バージョニング

## 新ドメイン追加手順

1. `domain/` → 2. `application/` → 3. `infrastructure/` → 4. `query/`(任意）
5. `app/app.py` でDI登録 → 6. `main.py` でCLI追加 → 7. `routers/` でAPI追加（任意）

イベント: `shared/event/` で定義 → `bootstrap()` でハンドラー登録

## cron定期実行

`scripts/cron-runner.sh <command>` で実行（`.env`読み込み・ログ出力を自動処理）。
`--notify` 付きでSlack通知。ログ: `/tmp/sandpiper-cron.log`

## 注意事項

- uvコマンドは必ず`uv run`プレフィックス使用(仮想環境自動活用)
- pyproject.toml直接編集せず`uv add`/`uv remove`使用
- テストは必ず`tests/`ディレクトリに配置、`test_*.py`命名

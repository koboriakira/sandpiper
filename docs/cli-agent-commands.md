# Sandpiper CLI — AIエージェント向けコマンド仕様

このドキュメントは、AIエージェント（チャットボット等）が Sandpiper CLI を使って
Notion 上のプロジェクト・プロジェクトタスク・TODO を操作するための仕様書です。

---

## 前提

- コマンド名: `sandpiper`
- 実行環境: `.env` が読み込まれた状態（`NOTION_SECRET` 等の環境変数が必要）
- 出力形式: `get` / `list` コマンドは **標準出力に JSON** を返す（パース可能）
- `update` コマンドは標準出力に人間向けの成功/エラーメッセージを返す
- 終了コード: 成功=0、失敗=1

---

## データモデル

### Project（プロジェクト）

| フィールド   | 型              | 説明                          |
| ----------- | --------------- | ----------------------------- |
| `id`        | string          | Notion ページ ID              |
| `name`      | string          | プロジェクト名                |
| `status`    | string \| null  | `"ToDo"` / `"InProgress"` / `"Done"` |
| `start_date`| string (YYYY-MM-DD) | 開始日                   |
| `end_date`  | string \| null  | 完了日 (YYYY-MM-DD)           |
| `jira_url`  | string \| null  | Jira チケット URL             |
| `claude_url`| string \| null  | Claude URL                    |

### ProjectTask（プロジェクトタスク）

| フィールド   | 型     | 説明                          |
| ----------- | ------ | ----------------------------- |
| `id`        | string | Notion ページ ID              |
| `title`     | string | タスクタイトル                |
| `status`    | string | `"ToDo"` / `"InProgress"` / `"Done"` |
| `project_id`| string | 親プロジェクトの Notion ID    |

### Todo（TODO）

| フィールド        | 型              | 説明                                        |
| ---------------- | --------------- | ------------------------------------------- |
| `id`             | string          | Notion ページ ID                            |
| `title`          | string          | タイトル                                    |
| `status`         | string          | `"ToDo"` / `"InProgress"` / `"Done"`        |
| `section`        | string \| null  | タスクシュートのセクション（後述）          |
| `scheduled_start`| string \| null  | 予定開始時刻 (ISO 8601)                     |
| `scheduled_end`  | string \| null  | 予定終了時刻 (ISO 8601)                     |
| `project_task_id`| string \| null  | 紐づくプロジェクトタスクの Notion ID        |
| `contexts`       | string[]        | コンテクスト一覧                            |

**Section の値:**

| 値          | 時間帯     |
| ----------- | ---------- |
| `A_07_10`   | 07:00–10:00 |
| `B_10_13`   | 10:00–13:00 |
| `C_13_17`   | 13:00–17:00 |
| `D_17_19`   | 17:00–19:00 |
| `E_19_22`   | 19:00–22:00 |
| `F_22_24`   | 22:00–24:00 |
| `G_24_07`   | 24:00–07:00 |

**Status の値（`--status` オプションで渡す文字列）:**

| オプション値  | JSON 出力値  | 意味         |
| ------------ | ----------- | ------------ |
| `TODO`       | `"ToDo"`    | 未着手       |
| `IN_PROGRESS`| `"InProgress"` | 進行中    |
| `DONE`       | `"Done"`    | 完了         |

---

## コマンドリファレンス

### `sandpiper project`

#### `project get <page_id>`

指定した Notion ID のプロジェクトを取得します。

```
sandpiper project get <page_id>
```

**出力例:**
```json
{
  "id": "abc123",
  "name": "新機能開発",
  "status": "InProgress",
  "start_date": "2026-01-15",
  "end_date": null,
  "jira_url": null,
  "claude_url": null
}
```

---

#### `project list`

全プロジェクトの一覧を取得します。

```
sandpiper project list [--status <STATUS>]
```

| オプション | 必須 | 説明                                      |
| --------- | ---- | ----------------------------------------- |
| `--status`| 任意 | `TODO` / `IN_PROGRESS` / `DONE` で絞り込み |

**出力例:**
```json
[
  {
    "id": "abc123",
    "name": "新機能開発",
    "status": "InProgress",
    "start_date": "2026-01-15",
    "end_date": null,
    "jira_url": null,
    "claude_url": null
  }
]
```

---

#### `project update <page_id>`

プロジェクトのプロパティを更新します。少なくとも1つのオプションが必要です。

```
sandpiper project update <page_id> [--status <STATUS>] [--name <NAME>] [--end-date <DATE>]
```

| オプション   | 必須 | 説明                              |
| ----------- | ---- | --------------------------------- |
| `--status`  | 任意 | `TODO` / `IN_PROGRESS` / `DONE`   |
| `--name`    | 任意 | 新しいプロジェクト名              |
| `--end-date`| 任意 | 完了日 `YYYY-MM-DD` 形式          |

**使用例:**
```bash
sandpiper project update abc123 --status DONE
sandpiper project update abc123 --status DONE --end-date 2026-03-08
sandpiper project update abc123 --name "リブランディング"
```

---

### `sandpiper project-task`

#### `project-task get <page_id>`

指定した Notion ID のプロジェクトタスクを取得します。

```
sandpiper project-task get <page_id>
```

**出力例:**
```json
{
  "id": "def456",
  "title": "APIエンドポイント実装",
  "status": "ToDo",
  "project_id": "abc123"
}
```

---

#### `project-task list`

プロジェクトタスクの一覧を取得します。

```
sandpiper project-task list [--project-id <ID>] [--status <STATUS>]
```

| オプション     | 必須 | 説明                                      |
| ------------- | ---- | ----------------------------------------- |
| `--project-id`| 任意 | 親プロジェクトの Notion ID で絞り込み     |
| `--status`    | 任意 | `TODO` / `IN_PROGRESS` / `DONE` で絞り込み |

**出力例:**
```json
[
  {
    "id": "def456",
    "title": "APIエンドポイント実装",
    "status": "ToDo",
    "project_id": "abc123"
  }
]
```

---

#### `project-task update <page_id>`

プロジェクトタスクのプロパティを更新します。少なくとも1つのオプションが必要です。

```
sandpiper project-task update <page_id> [--status <STATUS>] [--title <TITLE>]
```

| オプション | 必須 | 説明                            |
| --------- | ---- | ------------------------------- |
| `--status`| 任意 | `TODO` / `IN_PROGRESS` / `DONE` |
| `--title` | 任意 | 新しいタイトル                  |

**使用例:**
```bash
sandpiper project-task update def456 --status IN_PROGRESS
sandpiper project-task update def456 --title "API設計と実装"
```

---

### `sandpiper todo`

#### `todo get <page_id>`

指定した Notion ID の TODO を取得します。

```
sandpiper todo get <page_id>
```

**出力例:**
```json
{
  "id": "ghi789",
  "title": "デイリーレポート作成",
  "status": "ToDo",
  "section": "B_10_13",
  "scheduled_start": "2026-03-08T10:00:00+09:00",
  "scheduled_end": "2026-03-08T11:00:00+09:00",
  "project_task_id": "def456",
  "contexts": []
}
```

---

#### `todo list`

TODO の一覧を取得します。デフォルトはステータスが `ToDo` のものだけ返します。

```
sandpiper todo list [--status <STATUS>]
```

| オプション | 必須 | 説明 |
| --------- | ---- | ---- |
| `--status`| 任意 | `TODO`（デフォルト） / `IN_PROGRESS` / `DONE` / `ALL`（全件） |

**使用例:**
```bash
sandpiper todo list                     # ToDo ステータスのみ
sandpiper todo list --status IN_PROGRESS
sandpiper todo list --status ALL        # 全件取得
```

---

#### `todo update <page_id>`

TODO のプロパティを更新します。少なくとも1つのオプションが必要です。

```
sandpiper todo update <page_id> [--status <STATUS>] [--section <SECTION>] [--title <TITLE>]
```

| オプション  | 必須 | 説明 |
| ---------- | ---- | ---- |
| `--status` | 任意 | `TODO` / `IN_PROGRESS` / `DONE` |
| `--section`| 任意 | `A_07_10` / `B_10_13` / `C_13_17` / `D_17_19` / `E_19_22` / `F_22_24` / `G_24_07` |
| `--title`  | 任意 | 新しいタイトル |

**使用例:**
```bash
sandpiper todo update ghi789 --status DONE
sandpiper todo update ghi789 --section C_13_17
sandpiper todo update ghi789 --status IN_PROGRESS --section B_10_13
```

---

## エラーハンドリング

| 状況                         | 終了コード | 出力先   | 内容                          |
| ---------------------------- | ---------- | -------- | ----------------------------- |
| 正常終了                     | 0          | stdout   | JSON（get/list）または成功文  |
| 無効なステータス値            | 1          | stdout   | エラーメッセージ              |
| 無効な日付形式               | 1          | stdout   | エラーメッセージ              |
| オプションが1つも指定されない | 1          | stdout   | エラーメッセージ              |
| Notion API エラー            | 1          | stdout   | 例外メッセージ                |

---

## AIエージェント向け操作パターン例

### パターン1: プロジェクトを探してステータスを確認する

```bash
# 全プロジェクトを取得して名前で探す
sandpiper project list

# 特定プロジェクトの詳細を確認
sandpiper project get <id>
```

### パターン2: プロジェクトに紐づくタスク一覧を確認する

```bash
# プロジェクトIDを取得
sandpiper project list

# そのプロジェクトのタスク一覧
sandpiper project-task list --project-id <project_id>
```

### パターン3: 今日のTODOを確認して完了にする

```bash
# 未着手のTODO一覧
sandpiper todo list

# 完了にする
sandpiper todo update <id> --status DONE
```

### パターン4: 進行中のTODOをセクション変更する

```bash
# 進行中のTODO一覧
sandpiper todo list --status IN_PROGRESS

# セクションを変更
sandpiper todo update <id> --section C_13_17
```

### パターン5: プロジェクトを完了にして完了日を設定する

```bash
sandpiper project update <id> --status DONE --end-date 2026-03-08
```

---

## 注意事項

- `id` / `project_id` / `project_task_id` はすべて **Notion ページ ID**（UUID 形式）
- `status` のオプション入力値（`TODO` 等）と JSON 出力値（`"ToDo"` 等）は異なる
- `todo list` はデフォルトで **ToDo ステータスのみ**返す（全件取得は `--status ALL`）
- `todo list --status ALL` は件数が多い場合があるため、可能な限りフィルタを使うこと
- 複数プロパティを同時に更新できる（例: `--status DONE --end-date 2026-03-08`）

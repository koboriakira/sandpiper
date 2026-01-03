# Changelog

すべての注目すべき変更はこのファイルに記録されます。

このプロジェクトは[セマンティックバージョニング](https://semver.org/spec/v2.0.0.html)に従い、
[Conventional Commits](https://conventionalcommits.org/)を使用して自動的にリリースを生成します。

## 0.1.0 (2026-01-03)


### Features

* add .env.template with Notion secret and authorization token placeholders ([c2f242c](https://github.com/koboriakira/sandpiper/commit/c2f242c6ff68b11c9634dc8bcbe74f782e713fce))
* add create_repeat_tasks command and refactor CreateRepeatTask initialization ([5c0d375](https://github.com/koboriakira/sandpiper/commit/5c0d37575cbd3e4ca246f9d72c880d25115502a7))
* add fastapi ([373a1df](https://github.com/koboriakira/sandpiper/commit/373a1df26918f229809287903428480860bfa28e))
* add is_next attribute to ProjectTaskDto and update related query logic ([781fb6a](https://github.com/koboriakira/sandpiper/commit/781fb6ab3680272fc00b35e8667b3976153c3e11))
* add Notion API endpoints and authorization verification ([7513d46](https://github.com/koboriakira/sandpiper/commit/7513d46f0761f9f390e0df9404b5e00d0577f363))
* add NotionCommentator for project comments and update HandleCompletedTask to use it ([a4799c7](https://github.com/koboriakira/sandpiper/commit/a4799c71e83df5b978841bb52a6d9c9d65479a28))
* add option to create repeat project tasks for tomorrow ([db097b2](https://github.com/koboriakira/sandpiper/commit/db097b2c2bc0a50f24157c98776869863c0e3036))
* add ProjectTaskDto class and refactor ProjectTaskQuery to use it ([ff32d5f](https://github.com/koboriakira/sandpiper/commit/ff32d5f27b4f30a06a258eaf6d147881fcd03e98))
* add task management functionality with Notion integration ([487bdee](https://github.com/koboriakira/sandpiper/commit/487bdeece3c6d929e54c2831f67cec47a8cb2dc5))
* disable authorization verification for all endpoints in Notion router ([4891b85](https://github.com/koboriakira/sandpiper/commit/4891b854d0234e01d9289d7fe1704f13ed9922c2))
* enhance get_todo_log command to support JSON and Markdown output formats ([158b331](https://github.com/koboriakira/sandpiper/commit/158b331a4d612300333fa447ca07d5eb6b5771b4))
* enhance Slack message formatting to mention a user in notifications ([4f171e4](https://github.com/koboriakira/sandpiper/commit/4f171e4238b1df07c2e6e30b78b69e5880ee6c93))
* enhance todo logging to include project names and update NotionTodoQuery for project handling ([e70b0b6](https://github.com/koboriakira/sandpiper/commit/e70b0b69ef678d20708b3b30bf3b0cc48cf0e757))
* enhance TodoPage generation with rich text support for titles ([641af0a](https://github.com/koboriakira/sandpiper/commit/641af0a573f85afdd287444687597264dc4c4623))
* implement CompleteTodo functionality and add /todo/complete endpoint ([10a6b66](https://github.com/koboriakira/sandpiper/commit/10a6b661d664797e29853baa35de2db359c5e192))
* implement core ToDo functionality with Notion integration and event handling ([1510abb](https://github.com/koboriakira/sandpiper/commit/1510abbe9a9acef2ddff1b716a6beca21c55c807))
* implement create_repeat_project_task functionality and update related components ([9546148](https://github.com/koboriakira/sandpiper/commit/954614860c0a327f2f92c5fbde3decb92a0f95ef))
* implement GetTodoLog functionality and associated query classes ([ef71c3b](https://github.com/koboriakira/sandpiper/commit/ef71c3b36ac403d500ecb08e6c00328281c73b1f))
* implement handling of completed tasks and publish TodoCompleted event ([c54b201](https://github.com/koboriakira/sandpiper/commit/c54b2018210a0724a5a72f2faa9f8332cee857b8))
* implement routine management with Notion integration and add routine cycle functionality ([2b5e7df](https://github.com/koboriakira/sandpiper/commit/2b5e7df5053ba915c350539dee91f4fc764b0655))
* implement StartTodo functionality and add /todo/start endpoint ([bd69c82](https://github.com/koboriakira/sandpiper/commit/bd69c82e8f25bb78c0d1def72503b1ccb045626b))
* include task kind in the todo log output for better context ([e0676fe](https://github.com/koboriakira/sandpiper/commit/e0676fe06f3bc071999c090f186084a468d8de9e))
* integrate Slack notification system for completed tasks and add Slack SDK dependency ([7cda7ac](https://github.com/koboriakira/sandpiper/commit/7cda7ac798751e4d0c14f91b1f5ce138b36707df))
* refactor task handling by introducing next_todo_rule function for dynamic ToDo creation ([709754e](https://github.com/koboriakira/sandpiper/commit/709754ef1c0679f74ad3a476089bdd46cb445bca))
* refactor ToDo handling and integrate Notion repositories ([71a75c1](https://github.com/koboriakira/sandpiper/commit/71a75c1c964ecc5ad3c1924d968162cd48b0f598))
* rename inprogress method to start and streamline ToDo status handling ([bd560bd](https://github.com/koboriakira/sandpiper/commit/bd560bdd2b3329c33b8d443b9e7d57585b2efc34))
* SandPiperAppを注入 ([7f96e1c](https://github.com/koboriakira/sandpiper/commit/7f96e1caf2b97dafe40692b10b7cb6f881e578ad))
* update CLAUDE.md for project overview and architecture details ([f8c0186](https://github.com/koboriakira/sandpiper/commit/f8c0186aa45a14a0d7c0febf744407ae066d5b3a))
* update task handling for laundry completion with new follow-up tasks ([40e6216](https://github.com/koboriakira/sandpiper/commit/40e62165f98599ee9f4d9990e0a1c35ec3400d73))
* update ToDo and NotionTodoRepository to allow optional section and kind attributes ([8aa854d](https://github.com/koboriakira/sandpiper/commit/8aa854d23bfc23bbd37648049467345eb6c2ee21))


### Bug Fixes

* add type ignores for untyped calls and enhance type hints in various modules ([cf49c0f](https://github.com/koboriakira/sandpiper/commit/cf49c0f64d5fafa384dc8d222101004c5edc81de))
* correct argument name in query fixture for consistency ([1ba7f06](https://github.com/koboriakira/sandpiper/commit/1ba7f06c6e490703d691ae228edfc6d114a60df1))
* remove type ignores for NotionTodoRepository instantiation ([f65417f](https://github.com/koboriakira/sandpiper/commit/f65417f9e87285dc41f7c0b03cd387fd6157f45a))
* remove type ignores for untyped calls and enhance type hints in various modules ([08e76d1](https://github.com/koboriakira/sandpiper/commit/08e76d17b9d2a73ffe06c2a844c02b52bae8390a))
* update function signatures to use generic type parameters for date conversion functions ([63bcf78](https://github.com/koboriakira/sandpiper/commit/63bcf786fd8bb2053ace8209e31320b5adc76972))

## [0.2.0](https://github.com/koboriakira/sandpiper/compare/v0.1.1...v0.2.0) (2026-01-01)


### Features

* プロジェクトテンプレート化機能の実装 ([#11](https://github.com/koboriakira/sandpiper/issues/11)) ([50a3309](https://github.com/koboriakira/sandpiper/commit/50a3309976a643a9bd0c921940f729c48186e1dd))


### Bug Fixes

* Update README and install script for improved project setup instructions ([#13](https://github.com/koboriakira/sandpiper/issues/13)) ([7c5e88c](https://github.com/koboriakira/sandpiper/commit/7c5e88cfb8e7414195b5e275693d250f6adb0a8d))

## [0.1.1](https://github.com/koboriakira/sandpiper/compare/v0.1.0...v0.1.1) (2026-01-01)


### Bug Fixes

* TestPyPI Trusted Publisher用にenvironment設定を追加 ([#8](https://github.com/koboriakira/sandpiper/issues/8)) ([51a7431](https://github.com/koboriakira/sandpiper/commit/51a7431ff16fbdcc5e43c5faf825c76f1af02e83))

## 0.1.0 (2026-01-01)


### Features

* 2026年最新Python開発テンプレート初期作成 ([5981110](https://github.com/koboriakira/sandpiper/commit/59811108ece62d1b869abc820c55ec1b77cf13b0))


### Bug Fixes

* CIのセキュリティ監査でpip-auditが見つからない問題を修正 ([d623a65](https://github.com/koboriakira/sandpiper/commit/d623a6597347358220e3847a2048ef7d65477cdd))
* GitHub Actions CI依存関係インストールエラーを修正 ([#4](https://github.com/koboriakira/sandpiper/issues/4)) ([445af52](https://github.com/koboriakira/sandpiper/commit/445af520cc2756d331eceb9b595d72083d275b37))
* mypy設定のパッケージ名にスラッシュが含まれていた問題を修正 ([1324114](https://github.com/koboriakira/sandpiper/commit/132411404699aeab60881b83e00deb2656077cac))
* release-please GitHub Actions権限エラーを修正 ([#2](https://github.com/koboriakira/sandpiper/issues/2)) ([42f7871](https://github.com/koboriakira/sandpiper/commit/42f78712fb912d58245eb16769993decd0634de8))


### Documentation

* Claude Code機能統合とワークフロー最適化 ([#3](https://github.com/koboriakira/sandpiper/issues/3)) ([09af203](https://github.com/koboriakira/sandpiper/commit/09af2033e9cd0a3b79dda323e65b274e080158f7))
* Update GITHUB_SETUP.md to include Codecov configuration and error resolution ([#5](https://github.com/koboriakira/sandpiper/issues/5)) ([836c6e0](https://github.com/koboriakira/sandpiper/commit/836c6e01b306d3e74ab1de8f641e4061963c2a66))

## [Unreleased]

### Features

- 初期プロジェクト作成
- uv、ruff、pytest、mypy統合
- release-pleaseによる自動リリース管理
- CLIアプリケーション(typer + rich)
- 包括的なテストスイート
- GitHub Actions CI/CDパイプライン
- pre-commit品質管理フック

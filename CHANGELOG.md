# Changelog

すべての注目すべき変更はこのファイルに記録されます。

このプロジェクトは[セマンティックバージョニング](https://semver.org/spec/v2.0.0.html)に従い、
[Conventional Commits](https://conventionalcommits.org/)を使用して自動的にリリースを生成します。

## [0.19.0](https://github.com/koboriakira/sandpiper/compare/sandpiper-v0.18.0...sandpiper-v0.19.0) (2026-02-03)


### Features

* Add individual weekly and monthly routine cycles ([#108](https://github.com/koboriakira/sandpiper/issues/108)) ([fad83f1](https://github.com/koboriakira/sandpiper/commit/fad83f177745928693b64370accc9539fc634a8d))
* Add Notion embed component for in-progress TODO display ([87f58ef](https://github.com/koboriakira/sandpiper/commit/87f58ef7841ba94a732d4bd1abab429e4f40a4c4))
* Notion埋め込み用TODO表示API を追加 ([#109](https://github.com/koboriakira/sandpiper/issues/109)) ([87f58ef](https://github.com/koboriakira/sandpiper/commit/87f58ef7841ba94a732d4bd1abab429e4f40a4c4))
* RoutineCycleに新しい周期プロパティを追加 ([fad83f1](https://github.com/koboriakira/sandpiper/commit/fad83f177745928693b64370accc9539fc634a8d))
* カレンダーイベントの予定終了時刻をTODOに追加 ([#110](https://github.com/koboriakira/sandpiper/issues/110)) ([d6d2b70](https://github.com/koboriakira/sandpiper/commit/d6d2b705419de35019c348a670bab994d00a52f9))
* カレンダーからTODO作成時に予定時刻をコピー ([d6d2b70](https://github.com/koboriakira/sandpiper/commit/d6d2b705419de35019c348a670bab994d00a52f9))
* タスク終了時刻の予定通知機能を追加 ([#112](https://github.com/koboriakira/sandpiper/issues/112)) ([2260082](https://github.com/koboriakira/sandpiper/commit/22600826d97cf135e0a230e1e8827d1134f5666e))
* タスク開始時に所要時間経過後のSlack通知をスケジュール ([2260082](https://github.com/koboriakira/sandpiper/commit/22600826d97cf135e0a230e1e8827d1134f5666e))


### Code Refactoring

* Consolidate calendar date properties into single date range ([#111](https://github.com/koboriakira/sandpiper/issues/111)) ([b0569e8](https://github.com/koboriakira/sandpiper/commit/b0569e8182cd0a75a45c1665c7b64347e39343f3))
* Remove is_work field from Project domain ([#106](https://github.com/koboriakira/sandpiper/issues/106)) ([dd19526](https://github.com/koboriakira/sandpiper/commit/dd19526c5f2b11b068355b3f1fd2cff293c8e3a5))
* カレンダーデータベースの日時プロパティを統合 ([b0569e8](https://github.com/koboriakira/sandpiper/commit/b0569e8182cd0a75a45c1665c7b64347e39343f3))

## [0.18.0](https://github.com/koboriakira/sandpiper/compare/sandpiper-v0.17.0...sandpiper-v0.18.0) (2026-02-01)


### Features

* override_section_by_schedule に一括実行機能を追加 ([#104](https://github.com/koboriakira/sandpiper/issues/104)) ([e74a4cf](https://github.com/koboriakira/sandpiper/commit/e74a4cff7060c544e64ef12f2a3203ee5614df24))
* override-section-by-scheduleコマンドでpage_id省略時に全TODO処理 ([e74a4cf](https://github.com/koboriakira/sandpiper/commit/e74a4cff7060c544e64ef12f2a3203ee5614df24))

## [0.17.0](https://github.com/koboriakira/sandpiper/compare/sandpiper-v0.16.0...sandpiper-v0.17.0) (2026-02-01)


### Features

* Support date-only scheduling for tasks without specific times ([#103](https://github.com/koboriakira/sandpiper/issues/103)) ([f944d2f](https://github.com/koboriakira/sandpiper/commit/f944d2f87e27a0553ce81e0b11142f2ed14275f2))
* サムデイアイテム作成にタイミング・フラグ・コンテクスト機能を追加 ([#99](https://github.com/koboriakira/sandpiper/issues/99)) ([7aba5e8](https://github.com/koboriakira/sandpiper/commit/7aba5e8a2a934a033f0ac0b4f5e150a9abe4a76a))
* 予定開始時刻からセクションを上書きする機能を追加 ([#102](https://github.com/koboriakira/sandpiper/issues/102)) ([5594415](https://github.com/koboriakira/sandpiper/commit/55944155a04e1622b536224d801529a91d9859c8))


### Bug Fixes

* プロジェクトタスクからTODOコピー時に予定未定の場合は日付のみを設定 ([f944d2f](https://github.com/koboriakira/sandpiper/commit/f944d2f87e27a0553ce81e0b11142f2ed14275f2))


### Code Refactoring

* move domain models to shared layer for better reusability ([#101](https://github.com/koboriakira/sandpiper/issues/101)) ([629850a](https://github.com/koboriakira/sandpiper/commit/629850aefc21c2e91a0f0c0b462ad3cc2f2e560a))

## [0.16.0](https://github.com/koboriakira/sandpiper/compare/sandpiper-v0.15.0...sandpiper-v0.16.0) (2026-01-31)


### Features

* 日時を適宜計算してコピーする ([#95](https://github.com/koboriakira/sandpiper/issues/95)) ([0b7efe2](https://github.com/koboriakira/sandpiper/commit/0b7efe238bcc989b009663a0d979782cd240ccfe))


### Bug Fixes

* Add JST timezone to scheduled datetime creation ([#97](https://github.com/koboriakira/sandpiper/issues/97)) ([467da88](https://github.com/koboriakira/sandpiper/commit/467da88e0fbf6fdd5a8c89a31607b1b9542bf250))
* lint and format errors in test files and domain code ([333275f](https://github.com/koboriakira/sandpiper/commit/333275f7ea52962e2e2875ecc3eb35dbe2ea513b))
* TODOの予定プロパティをJSTタイムゾーンでコピーする ([467da88](https://github.com/koboriakira/sandpiper/commit/467da88e0fbf6fdd5a8c89a31607b1b9542bf250))

## [0.15.0](https://github.com/koboriakira/sandpiper/compare/sandpiper-v0.14.0...sandpiper-v0.15.0) (2026-01-31)


### Features

* Add scheduled_date field to tasks and routines ([#93](https://github.com/koboriakira/sandpiper/issues/93)) ([dfbe21c](https://github.com/koboriakira/sandpiper/commit/dfbe21c37b8a5fce3540963850a3cc0026e49c07))
* 土日の仕事系プロジェクトタスク自動除外機能を追加 ([#92](https://github.com/koboriakira/sandpiper/issues/92)) ([fcc7e00](https://github.com/koboriakira/sandpiper/commit/fcc7e00352b6ebcd026f14aa5cc08d753aac4f9b))

## [0.14.0](https://github.com/koboriakira/sandpiper/compare/sandpiper-v0.13.0...sandpiper-v0.14.0) (2026-01-31)


### Features

* Notion側にのみ存在するプロジェクトの検出機能を追加 ([#91](https://github.com/koboriakira/sandpiper/issues/91)) ([a7b0c81](https://github.com/koboriakira/sandpiper/commit/a7b0c81a0baa55dba1329eff27e4d95c9a5583a1))
* Show Notion-only projects in SyncJiraToProject output ([a7b0c81](https://github.com/koboriakira/sandpiper/commit/a7b0c81a0baa55dba1329eff27e4d95c9a5583a1))
* カレンダーイベントからスケジュールタスクを自動作成 ([#88](https://github.com/koboriakira/sandpiper/issues/88)) ([f1e6937](https://github.com/koboriakira/sandpiper/commit/f1e6937adee23a320e8749431716947d2ace4828))
* 明日のTODOリスト作成時に論理削除ページをアーカイブ ([28af85d](https://github.com/koboriakira/sandpiper/commit/28af85df2cf037e817c739f15f1cb51475fa0a5d))


### Bug Fixes

* **ci:** ignore CVE-2026-0994 in pip-audit until fix is available ([2e417d2](https://github.com/koboriakira/sandpiper/commit/2e417d23ee85b3ea8cfa120dfa4764c2ea6d2263))
* Correct property name for ProjectEndDate from "終了日" to "締切日" ([#85](https://github.com/koboriakira/sandpiper/issues/85)) ([9507e46](https://github.com/koboriakira/sandpiper/commit/9507e46d0d09084bad3ab8795bac0e21f6305c34))


### Code Refactoring

* Inject ArchiveDeletedPages into HandleSpecialTodo ([#87](https://github.com/koboriakira/sandpiper/issues/87)) ([28af85d](https://github.com/koboriakira/sandpiper/commit/28af85df2cf037e817c739f15f1cb51475fa0a5d))

## [0.13.0](https://github.com/koboriakira/sandpiper/compare/sandpiper-v0.12.0...sandpiper-v0.13.0) (2026-01-24)


### Features

* Add additional statuses to ToDoStatusEnum ([#79](https://github.com/koboriakira/sandpiper/issues/79)) ([03365b0](https://github.com/koboriakira/sandpiper/commit/03365b0d07b84bf3797d43824df68ee0dd86f516))
* Add CLI command for creating TODOs from someday list ([3c3a521](https://github.com/koboriakira/sandpiper/commit/3c3a521cdd622be20b24630a10e98e9432060ffc))
* Add is_work checkbox field to Project ([#82](https://github.com/koboriakira/sandpiper/issues/82)) ([fc18c44](https://github.com/koboriakira/sandpiper/commit/fc18c448d2f1a8e66afd0b87f4b9a9843403d956))
* Add is_work property support to Project domain ([fc18c44](https://github.com/koboriakira/sandpiper/commit/fc18c448d2f1a8e66afd0b87f4b9a9843403d956))
* サムデイリストから TODO を作成する機能を追加 ([#83](https://github.com/koboriakira/sandpiper/issues/83)) ([3c3a521](https://github.com/koboriakira/sandpiper/commit/3c3a521cdd622be20b24630a10e98e9432060ffc))


### Bug Fixes

* Simplify update and delete methods in NotionSomedayRepository; e… ([#84](https://github.com/koboriakira/sandpiper/issues/84)) ([84416af](https://github.com/koboriakira/sandpiper/commit/84416af3e4f0a5430f4056e7cb294513b9ab8147))
* Simplify update and delete methods in NotionSomedayRepository; enhance SomedayPage attributes ([84416af](https://github.com/koboriakira/sandpiper/commit/84416af3e4f0a5430f4056e7cb294513b9ab8147))


### Documentation

* Add detailed description to /todo/special endpoint ([7795b85](https://github.com/koboriakira/sandpiper/commit/7795b858d3fc662fda78962ce6ecbf320f2c5bcc))
* Notion webhook エンドポイントのドキュメント拡充 ([#81](https://github.com/koboriakira/sandpiper/issues/81)) ([7795b85](https://github.com/koboriakira/sandpiper/commit/7795b858d3fc662fda78962ce6ecbf320f2c5bcc))

## [0.12.0](https://github.com/koboriakira/sandpiper/compare/sandpiper-v0.11.0...sandpiper-v0.12.0) (2026-01-20)


### Features

* Exclude project tasks from ToDo-status projects ([39b4782](https://github.com/koboriakira/sandpiper/commit/39b478214476c88dde76b35a9b5917698eaf24d9))
* Exclude ToDo status project tasks from creation ([#77](https://github.com/koboriakira/sandpiper/issues/77)) ([39b4782](https://github.com/koboriakira/sandpiper/commit/39b478214476c88dde76b35a9b5917698eaf24d9))


### Bug Fixes

* Add debug mode to CreateRepeatTask and update NotionTodoRepository to handle sort order ([e9bd94c](https://github.com/koboriakira/sandpiper/commit/e9bd94c3fa072087d019cbba70eb63bcf7ce7f27))
* Add type ignore comments for googleapiclient untyped imports ([cd6b92b](https://github.com/koboriakira/sandpiper/commit/cd6b92b9c370697598af3f81abfea2238aaba084))
* Fix/todo sort order ([#75](https://github.com/koboriakira/sandpiper/issues/75)) ([e9bd94c](https://github.com/koboriakira/sandpiper/commit/e9bd94c3fa072087d019cbba70eb63bcf7ce7f27))

## [0.11.0](https://github.com/koboriakira/sandpiper/compare/sandpiper-v0.10.0...sandpiper-v0.11.0) (2026-01-18)


### Features

* add .env.template with Notion secret and authorization token placeholders ([c2f242c](https://github.com/koboriakira/sandpiper/commit/c2f242c6ff68b11c9634dc8bcbe74f782e713fce))
* Add archive endpoint for Notion deleted items ([#34](https://github.com/koboriakira/sandpiper/issues/34)) ([f92caf7](https://github.com/koboriakira/sandpiper/commit/f92caf7078b58615bbb5988f144aed1a6299b054))
* Add archive functionality for completed todos older than 7 days ([#66](https://github.com/koboriakira/sandpiper/issues/66)) ([0020bb9](https://github.com/koboriakira/sandpiper/commit/0020bb997bd556eee30691590f323215c7348b7e))
* Add auto_fetch_title property for clips ([#42](https://github.com/koboriakira/sandpiper/issues/42)) ([ae668c6](https://github.com/koboriakira/sandpiper/commit/ae668c664d6934aab77487e2839fc6f61f50a96f))
* Add context property to Notion databases ([#35](https://github.com/koboriakira/sandpiper/issues/35)) ([067f13c](https://github.com/koboriakira/sandpiper/commit/067f13c7920cb9893238799d473289dfdccea72f))
* Add context property to someday list database ([#40](https://github.com/koboriakira/sandpiper/issues/40)) ([91984f1](https://github.com/koboriakira/sandpiper/commit/91984f10b0b13e83db6934be3881c493a76cce95))
* Add convert TODO to project feature ([#13](https://github.com/koboriakira/sandpiper/issues/13)) ([2f4414b](https://github.com/koboriakira/sandpiper/commit/2f4414ba442e75baca7eac32dbdac3aef220c2b4))
* add create_repeat_tasks command and refactor CreateRepeatTask initialization ([5c0d375](https://github.com/koboriakira/sandpiper/commit/5c0d37575cbd3e4ca246f9d72c880d25115502a7))
* Add create-someday CLI command for adding someday list items ([#43](https://github.com/koboriakira/sandpiper/issues/43)) ([63571b7](https://github.com/koboriakira/sandpiper/commit/63571b75a87032b0340353386da3e7907a892a6d))
* Add create-todo-next-section command for adding todos to next time section ([#58](https://github.com/koboriakira/sandpiper/issues/58)) ([55a7fc9](https://github.com/koboriakira/sandpiper/commit/55a7fc976b67c800bc3c6ccca260e30be3dcca44))
* Add date filtering for completed todos ([#19](https://github.com/koboriakira/sandpiper/issues/19)) ([dcf8f46](https://github.com/koboriakira/sandpiper/commit/dcf8f4606c59adaa6c0cbaa335d1809aa3b6d1b3))
* Add dish-related tasks to HandleCompletedTask ([#29](https://github.com/koboriakira/sandpiper/issues/29)) ([3a6de11](https://github.com/koboriakira/sandpiper/commit/3a6de1157a319df1a990192a35720ebbf9f572a3))
* add endpoint to convert Todo to Project and update version to 0.3.0 ([ee20da1](https://github.com/koboriakira/sandpiper/commit/ee20da1bf58be75826c7d33c868fc97b9dd65965))
* add fastapi ([373a1df](https://github.com/koboriakira/sandpiper/commit/373a1df26918f229809287903428480860bfa28e))
* Add import-linter for DDD layer dependency enforcement ([#53](https://github.com/koboriakira/sandpiper/issues/53)) ([298b08a](https://github.com/koboriakira/sandpiper/commit/298b08a63a9d0f344056f3952170aa189b0e097c))
* Add In Progress status when syncing JIRA tickets to projects ([#64](https://github.com/koboriakira/sandpiper/issues/64)) ([843897c](https://github.com/koboriakira/sandpiper/commit/843897c03fd3af24b8058f4d5f4b69f4eff45eea))
* Add inbox type detection for Notion clips API ([#37](https://github.com/koboriakira/sandpiper/issues/37)) ([277983e](https://github.com/koboriakira/sandpiper/commit/277983e348f4d7872cab6b2881da25f6fdfe3d62))
* add is_next attribute to ProjectTaskDto and update related query logic ([781fb6a](https://github.com/koboriakira/sandpiper/commit/781fb6ab3680272fc00b35e8667b3976153c3e11))
* Add JIRA ticket search and retrieval functionality ([#31](https://github.com/koboriakira/sandpiper/issues/31)) ([7085fc4](https://github.com/koboriakira/sandpiper/commit/7085fc4de6ab5b180dc4aaee41585876e5966305))
* Add Jira tickets to Notion projects ([#32](https://github.com/koboriakira/sandpiper/issues/32)) ([2ca4398](https://github.com/koboriakira/sandpiper/commit/2ca43981be60a8b806ad0f425314fe97d07f7fbc))
* add maintenance router and integrate with FastAPI application ([0ef46c2](https://github.com/koboriakira/sandpiper/commit/0ef46c291aeefab6cd63582bf5f5d79c1d47993e))
* add Notion API endpoints and authorization verification ([7513d46](https://github.com/koboriakira/sandpiper/commit/7513d46f0761f9f390e0df9404b5e00d0577f363))
* add NotionCommentator for project comments and update HandleCompletedTask to use it ([a4799c7](https://github.com/koboriakira/sandpiper/commit/a4799c71e83df5b978841bb52a6d9c9d65479a28))
* add option to create repeat project tasks for tomorrow ([db097b2](https://github.com/koboriakira/sandpiper/commit/db097b2c2bc0a50f24157c98776869863c0e3036))
* Add POST /api/notion/clips endpoint for creating web clips ([#36](https://github.com/koboriakira/sandpiper/issues/36)) ([9a26828](https://github.com/koboriakira/sandpiper/commit/9a26828fd16c45d2628a953f990b4f35eef4c736))
* add ProjectTaskDto class and refactor ProjectTaskQuery to use it ([ff32d5f](https://github.com/koboriakira/sandpiper/commit/ff32d5f27b4f30a06a258eaf6d147881fcd03e98))
* add response logging middleware to log response details ([5183723](https://github.com/koboriakira/sandpiper/commit/5183723592560ce566dc42a67350d0dc664e8e36))
* Add routine_page_id property to ToDo class ([#44](https://github.com/koboriakira/sandpiper/issues/44)) ([5356276](https://github.com/koboriakira/sandpiper/commit/5356276a12ae5c68cd0d4eee2358726446c4af9b))
* Add routine_page_id when creating repeat task todo ([#59](https://github.com/koboriakira/sandpiper/issues/59)) ([b8004a0](https://github.com/koboriakira/sandpiper/commit/b8004a0422e3e26fd8c18bde74a142ffd3364b15))
* Add skincare todo creation after bathing completion ([#61](https://github.com/koboriakira/sandpiper/issues/61)) ([284d3ed](https://github.com/koboriakira/sandpiper/commit/284d3ed8b215d7a98716b81a2deb0a5fbf335943))
* Add soft delete support for project tasks ([#57](https://github.com/koboriakira/sandpiper/issues/57)) ([4a5a80c](https://github.com/koboriakira/sandpiper/commit/4a5a80cd75a14103ff075b00d6337524f14eb717))
* Add sort order property to all task types ([#65](https://github.com/koboriakira/sandpiper/issues/65)) ([58de7c7](https://github.com/koboriakira/sandpiper/commit/58de7c7cae63cfa6296b637f2cda6741661251ab))
* add special todo handler endpoint for name-based processing ([#14](https://github.com/koboriakira/sandpiper/issues/14)) ([b323af6](https://github.com/koboriakira/sandpiper/commit/b323af6131207bd9b68cf38ccf96ed4727c0b435))
* add task management functionality with Notion integration ([487bdee](https://github.com/koboriakira/sandpiper/commit/487bdeece3c6d929e54c2831f67cec47a8cb2dc5))
* Add YouTube title fetching with Google API ([#71](https://github.com/koboriakira/sandpiper/issues/71)) ([f9efb1e](https://github.com/koboriakira/sandpiper/commit/f9efb1e814b1743dc14659eaf37eb2d1dd84d16d))
* Auto-merge release-please PRs after CI passes ([#68](https://github.com/koboriakira/sandpiper/issues/68)) ([95eac90](https://github.com/koboriakira/sandpiper/commit/95eac908fb16e405bca6ead9d2e7ea6726892b5f))
* calendar domain implementation with Notion integration ([#4](https://github.com/koboriakira/sandpiper/issues/4)) ([f415173](https://github.com/koboriakira/sandpiper/commit/f4151737586604a8a99bb6759458a60e39a3122c))
* Copy block content when creating repeat tasks ([#22](https://github.com/koboriakira/sandpiper/issues/22)) ([08c23d3](https://github.com/koboriakira/sandpiper/commit/08c23d38e0f937c0350280098186088f736435ca))
* Copy execution time when creating repeat tasks ([#21](https://github.com/koboriakira/sandpiper/issues/21)) ([558d3df](https://github.com/koboriakira/sandpiper/commit/558d3dfdbcc8e323ae9193e241e81ea55e31fb2a))
* Create CLI command for Notion recipe pages ([#23](https://github.com/koboriakira/sandpiper/issues/23)) ([8fa1fcf](https://github.com/koboriakira/sandpiper/commit/8fa1fcf9da49b121be76cb7db4c93a157380c96f))
* Create handler for TODO start events ([#48](https://github.com/koboriakira/sandpiper/issues/48)) ([6f508ca](https://github.com/koboriakira/sandpiper/commit/6f508ca2f3700a3bebc896d405322fd28cb61d1b))
* Create recipe context and add recipes ([#20](https://github.com/koboriakira/sandpiper/issues/20)) ([005ee2e](https://github.com/koboriakira/sandpiper/commit/005ee2e56864a6e7831f650123f74b23d5f678e6))
* Create recipe registration screen with API ([#60](https://github.com/koboriakira/sandpiper/issues/60)) ([95bda9e](https://github.com/koboriakira/sandpiper/commit/95bda9e5f6e1d94c878635cb8c9cd6c7d5fbc0f6))
* disable authorization verification for all endpoints in Notion router ([4891b85](https://github.com/koboriakira/sandpiper/commit/4891b854d0234e01d9289d7fe1704f13ed9922c2))
* enhance get_todo_log command to support JSON and Markdown output formats ([158b331](https://github.com/koboriakira/sandpiper/commit/158b331a4d612300333fa447ca07d5eb6b5771b4))
* enhance Slack message formatting to mention a user in notifications ([4f171e4](https://github.com/koboriakira/sandpiper/commit/4f171e4238b1df07c2e6e30b78b69e5880ee6c93))
* enhance todo logging to include project names and update NotionTodoQuery for project handling ([e70b0b6](https://github.com/koboriakira/sandpiper/commit/e70b0b69ef678d20708b3b30bf3b0cc48cf0e757))
* Enhance TodoPage generation with block content retrieval ([#46](https://github.com/koboriakira/sandpiper/issues/46)) ([5350fbe](https://github.com/koboriakira/sandpiper/commit/5350fbea448ced33b969c5cfe0571750c9776a4c))
* enhance TodoPage generation with rich text support for titles ([641af0a](https://github.com/koboriakira/sandpiper/commit/641af0a573f85afdd287444687597264dc4c4623))
* Execute ArchiveDeletedPages before create-repeat-tasks ([#67](https://github.com/koboriakira/sandpiper/issues/67)) ([db50765](https://github.com/koboriakira/sandpiper/commit/db507651d5721fa49ff9bc2d71170d7e449b02fd))
* Filter repeat task duplicates by "今日中にやる" property ([#26](https://github.com/koboriakira/sandpiper/issues/26)) ([c84cdba](https://github.com/koboriakira/sandpiper/commit/c84cdbaedf43f19f0f97844566a7da934a0af36f))
* GitHub活動ログ取得機能の追加 ([#2](https://github.com/koboriakira/sandpiper/issues/2)) ([9feef32](https://github.com/koboriakira/sandpiper/commit/9feef32a887a040b3bda3e42e02a84cb768173eb))
* implement CompleteTodo functionality and add /todo/complete endpoint ([10a6b66](https://github.com/koboriakira/sandpiper/commit/10a6b661d664797e29853baa35de2db359c5e192))
* implement core ToDo functionality with Notion integration and event handling ([1510abb](https://github.com/koboriakira/sandpiper/commit/1510abbe9a9acef2ddff1b716a6beca21c55c807))
* implement create_repeat_project_task functionality and update related components ([9546148](https://github.com/koboriakira/sandpiper/commit/954614860c0a327f2f92c5fbde3decb92a0f95ef))
* implement GetTodoLog functionality and associated query classes ([ef71c3b](https://github.com/koboriakira/sandpiper/commit/ef71c3b36ac403d500ecb08e6c00328281c73b1f))
* implement handling of completed tasks and publish TodoCompleted event ([c54b201](https://github.com/koboriakira/sandpiper/commit/c54b2018210a0724a5a72f2faa9f8332cee857b8))
* implement routine management with Notion integration and add routine cycle functionality ([2b5e7df](https://github.com/koboriakira/sandpiper/commit/2b5e7df5053ba915c350539dee91f4fc764b0655))
* implement StartTodo functionality and add /todo/start endpoint ([bd69c82](https://github.com/koboriakira/sandpiper/commit/bd69c82e8f25bb78c0d1def72503b1ccb045626b))
* include task kind in the todo log output for better context ([e0676fe](https://github.com/koboriakira/sandpiper/commit/e0676fe06f3bc071999c090f186084a468d8de9e))
* integrate Slack notification system for completed tasks and add Slack SDK dependency ([7cda7ac](https://github.com/koboriakira/sandpiper/commit/7cda7ac798751e4d0c14f91b1f5ce138b36707df))
* Make clip title optional and auto-fetch from URL ([#38](https://github.com/koboriakira/sandpiper/issues/38)) ([c9bd716](https://github.com/koboriakira/sandpiper/commit/c9bd716e7aaaeef777b72b96285429d58b2e0736))
* Make Notion webhook endpoints async with BackgroundTasks ([#62](https://github.com/koboriakira/sandpiper/issues/62)) ([5ec64b9](https://github.com/koboriakira/sandpiper/commit/5ec64b9668971cf9d3251bd648cdc1248ac21ff5))
* Publish event when todo starts ([#52](https://github.com/koboriakira/sandpiper/issues/52)) ([e5bc20b](https://github.com/koboriakira/sandpiper/commit/e5bc20b69f7d28df409932cffcf3522472da968c))
* refactor task handling by introducing next_todo_rule function for dynamic ToDo creation ([709754e](https://github.com/koboriakira/sandpiper/commit/709754ef1c0679f74ad3a476089bdd46cb445bca))
* refactor ToDo handling and integrate Notion repositories ([71a75c1](https://github.com/koboriakira/sandpiper/commit/71a75c1c964ecc5ad3c1924d968162cd48b0f598))
* rename inprogress method to start and streamline ToDo status handling ([bd560bd](https://github.com/koboriakira/sandpiper/commit/bd560bdd2b3329c33b8d443b9e7d57585b2efc34))
* SandPiperAppを注入 ([7f96e1c](https://github.com/koboriakira/sandpiper/commit/7f96e1caf2b97dafe40692b10b7cb6f881e578ad))
* Set up Notion database management for SomeDay list ([#27](https://github.com/koboriakira/sandpiper/issues/27)) ([31fb82e](https://github.com/koboriakira/sandpiper/commit/31fb82ebc74e079497cf28d80c19db210a817e70))
* Update CalendarEventPage to use date range for event start and end dates ([#30](https://github.com/koboriakira/sandpiper/issues/30)) ([093640c](https://github.com/koboriakira/sandpiper/commit/093640c8bce30f2de71cb7e851f333ee5f051f6f))
* update CLAUDE.md for project overview and architecture details ([f8c0186](https://github.com/koboriakira/sandpiper/commit/f8c0186aa45a14a0d7c0febf744407ae066d5b3a))
* Update project task status to in progress ([#16](https://github.com/koboriakira/sandpiper/issues/16)) ([64c68aa](https://github.com/koboriakira/sandpiper/commit/64c68aa3dad62d00ec2b6549b8acfd25c3d357ed))
* update task handling for laundry completion with new follow-up tasks ([40e6216](https://github.com/koboriakira/sandpiper/commit/40e62165f98599ee9f4d9990e0a1c35ec3400d73))
* update ToDo and NotionTodoRepository to allow optional section and kind attributes ([8aa854d](https://github.com/koboriakira/sandpiper/commit/8aa854d23bfc23bbd37648049467345eb6c2ee21))
* カレンダー削除APIエンドポイント実装 ([#5](https://github.com/koboriakira/sandpiper/issues/5)) ([fb69391](https://github.com/koboriakira/sandpiper/commit/fb69391cd8bac2be43c08ed5aefcc53824466576))
* プロジェクトタスクのデータベース操作 ([#11](https://github.com/koboriakira/sandpiper/issues/11)) ([ff05907](https://github.com/koboriakira/sandpiper/commit/ff059070b92fc41ac155a153d45057337fea7a22))
* プロジェクトデータベースの更新をする ([#9](https://github.com/koboriakira/sandpiper/issues/9)) ([7410771](https://github.com/koboriakira/sandpiper/commit/7410771df888a004d0106d233e52f6460728537e))


### Bug Fixes

* add type ignores for untyped calls and enhance type hints in various modules ([cf49c0f](https://github.com/koboriakira/sandpiper/commit/cf49c0f64d5fafa384dc8d222101004c5edc81de))
* correct argument name in query fixture for consistency ([1ba7f06](https://github.com/koboriakira/sandpiper/commit/1ba7f06c6e490703d691ae228edfc6d114a60df1))
* Fix CI/CD pipeline failures ([#50](https://github.com/koboriakira/sandpiper/issues/50)) ([94ffa7f](https://github.com/koboriakira/sandpiper/commit/94ffa7f114fe9bb85d438313d0508e123fd67349))
* improve event deletion logic and refactor category assignment ([ed81985](https://github.com/koboriakira/sandpiper/commit/ed819853d7e76aaea16ecaea41432977ae33e59f))
* remove type ignores for NotionTodoRepository instantiation ([f65417f](https://github.com/koboriakira/sandpiper/commit/f65417f9e87285dc41f7c0b03cd387fd6157f45a))
* remove type ignores for untyped calls and enhance type hints in various modules ([08e76d1](https://github.com/koboriakira/sandpiper/commit/08e76d17b9d2a73ffe06c2a844c02b52bae8390a))
* rename unused test parameter to satisfy ruff ARG002 ([#15](https://github.com/koboriakira/sandpiper/issues/15)) ([3dac3ea](https://github.com/koboriakira/sandpiper/commit/3dac3eaa28b4a591ada4058ec0e7280f776827b8))
* Reorder import-linter layers for CQRS pattern ([#56](https://github.com/koboriakira/sandpiper/issues/56)) ([405196a](https://github.com/koboriakira/sandpiper/commit/405196a63dd59484103717dbbcaeffe66cf20c69))
* TODOリスト作成の時刻ロジックを改善しルーチンタスクも追加 ([#17](https://github.com/koboriakira/sandpiper/issues/17)) ([3cff0cb](https://github.com/koboriakira/sandpiper/commit/3cff0cbab34a20c5845f24e3a5893316afd251c4))
* Update DATABASE_ID to the actual Notion Clips Database ID ([#39](https://github.com/koboriakira/sandpiper/issues/39)) ([243ef6a](https://github.com/koboriakira/sandpiper/commit/243ef6a2c31b131fac36a0d89f0bf7bc5691ba58))
* Update filelock and virtualenv to address security vulnerabilities ([#63](https://github.com/koboriakira/sandpiper/issues/63)) ([65b729a](https://github.com/koboriakira/sandpiper/commit/65b729a435a18a8f334fc1f1ff68b5a01be8a330))
* update function signatures to use generic type parameters for date conversion functions ([63bcf78](https://github.com/koboriakira/sandpiper/commit/63bcf786fd8bb2053ace8209e31320b5adc76972))
* update logic to process routine tasks only if the date is today or earlier ([2991321](https://github.com/koboriakira/sandpiper/commit/2991321a870e1ec2ecf66141bf709c01a1e48e6b))
* update routine processing logic to skip tasks with future dates and improve logging ([22eb3ec](https://github.com/koboriakira/sandpiper/commit/22eb3ec170802c588117e70960fd5b6e6bf4fcab))
* Upgrade urllib3 to 2.6.3 to fix CVE-2026-21441 ([#28](https://github.com/koboriakira/sandpiper/issues/28)) ([ab63f21](https://github.com/koboriakira/sandpiper/commit/ab63f2120b07d59a9e2b5f03116e7a03d749fbd2))


### Documentation

* Update README and CLAUDE.md to reflect new features and project structure ([#49](https://github.com/koboriakira/sandpiper/issues/49)) ([454d5a5](https://github.com/koboriakira/sandpiper/commit/454d5a57180f0531577f48dceeceb7588f716a59))


### Code Refactoring

* add type hints and ignore directives across multiple modules ([f4415ca](https://github.com/koboriakira/sandpiper/commit/f4415caa76ad8aad0af258735bc65d1e95262632))
* Improve date_utils module with modern Python patterns ([#51](https://github.com/koboriakira/sandpiper/issues/51)) ([d96088b](https://github.com/koboriakira/sandpiper/commit/d96088b3e0ac028ca38abc67589cbb1879433d23))
* Refactor Notion Someday repository to use database class ([#47](https://github.com/koboriakira/sandpiper/issues/47)) ([39378d8](https://github.com/koboriakira/sandpiper/commit/39378d8644799d0e943816bfce34a37643c5cdb1))
* Refactor test cases for consistency and readability ([6c7d903](https://github.com/koboriakira/sandpiper/commit/6c7d903d895c927df3dab2fc583902515e9be52b))
* Refactor test files to improve readability and consistency ([290e1ce](https://github.com/koboriakira/sandpiper/commit/290e1ceff0aebefe5aad52c674135830ea2f73bf))
* Rename event classes for consistency ([#55](https://github.com/koboriakira/sandpiper/issues/55)) ([a334cf1](https://github.com/koboriakira/sandpiper/commit/a334cf16d032110eaaf1211b6b34f6325017f95c))
* rename TodoKind to TodoKindProp for consistency in Notion properties ([97bdedc](https://github.com/koboriakira/sandpiper/commit/97bdedc6832ceec64f2eb008780b45eaf30bd825))
* Reorganize Notion config by database ([#33](https://github.com/koboriakira/sandpiper/issues/33)) ([4433aef](https://github.com/koboriakira/sandpiper/commit/4433aeffaff6b5ac77d0ce74262155c3ce30ff1b))
* unify parentheses style in descriptions and comments across multiple files ([98d892f](https://github.com/koboriakira/sandpiper/commit/98d892f7f289833d78983a22dd157e18b4ac37e9))

## [0.10.0](https://github.com/koboriakira/sandpiper/compare/v0.9.0...v0.10.0) (2026-01-16)


### Features

* Add archive functionality for completed todos older than 7 days ([#66](https://github.com/koboriakira/sandpiper/issues/66)) ([0020bb9](https://github.com/koboriakira/sandpiper/commit/0020bb997bd556eee30691590f323215c7348b7e))
* Add create-todo-next-section command for adding todos to next time section ([#58](https://github.com/koboriakira/sandpiper/issues/58)) ([55a7fc9](https://github.com/koboriakira/sandpiper/commit/55a7fc976b67c800bc3c6ccca260e30be3dcca44))
* Add import-linter for DDD layer dependency enforcement ([#53](https://github.com/koboriakira/sandpiper/issues/53)) ([298b08a](https://github.com/koboriakira/sandpiper/commit/298b08a63a9d0f344056f3952170aa189b0e097c))
* Add In Progress status when syncing JIRA tickets to projects ([#64](https://github.com/koboriakira/sandpiper/issues/64)) ([843897c](https://github.com/koboriakira/sandpiper/commit/843897c03fd3af24b8058f4d5f4b69f4eff45eea))
* Add routine_page_id when creating repeat task todo ([#59](https://github.com/koboriakira/sandpiper/issues/59)) ([b8004a0](https://github.com/koboriakira/sandpiper/commit/b8004a0422e3e26fd8c18bde74a142ffd3364b15))
* Add skincare todo creation after bathing completion ([#61](https://github.com/koboriakira/sandpiper/issues/61)) ([284d3ed](https://github.com/koboriakira/sandpiper/commit/284d3ed8b215d7a98716b81a2deb0a5fbf335943))
* Add soft delete support for project tasks ([#57](https://github.com/koboriakira/sandpiper/issues/57)) ([4a5a80c](https://github.com/koboriakira/sandpiper/commit/4a5a80cd75a14103ff075b00d6337524f14eb717))
* Add sort order property to all task types ([#65](https://github.com/koboriakira/sandpiper/issues/65)) ([58de7c7](https://github.com/koboriakira/sandpiper/commit/58de7c7cae63cfa6296b637f2cda6741661251ab))
* Create recipe registration screen with API ([#60](https://github.com/koboriakira/sandpiper/issues/60)) ([95bda9e](https://github.com/koboriakira/sandpiper/commit/95bda9e5f6e1d94c878635cb8c9cd6c7d5fbc0f6))
* Make Notion webhook endpoints async with BackgroundTasks ([#62](https://github.com/koboriakira/sandpiper/issues/62)) ([5ec64b9](https://github.com/koboriakira/sandpiper/commit/5ec64b9668971cf9d3251bd648cdc1248ac21ff5))
* Publish event when todo starts ([#52](https://github.com/koboriakira/sandpiper/issues/52)) ([e5bc20b](https://github.com/koboriakira/sandpiper/commit/e5bc20b69f7d28df409932cffcf3522472da968c))


### Bug Fixes

* Reorder import-linter layers for CQRS pattern ([#56](https://github.com/koboriakira/sandpiper/issues/56)) ([405196a](https://github.com/koboriakira/sandpiper/commit/405196a63dd59484103717dbbcaeffe66cf20c69))
* Update filelock and virtualenv to address security vulnerabilities ([#63](https://github.com/koboriakira/sandpiper/issues/63)) ([65b729a](https://github.com/koboriakira/sandpiper/commit/65b729a435a18a8f334fc1f1ff68b5a01be8a330))

## [0.9.0](https://github.com/koboriakira/sandpiper/compare/v0.8.0...v0.9.0) (2026-01-12)


### Features

* Create handler for TODO start events ([#48](https://github.com/koboriakira/sandpiper/issues/48)) ([6f508ca](https://github.com/koboriakira/sandpiper/commit/6f508ca2f3700a3bebc896d405322fd28cb61d1b))
* Enhance TodoPage generation with block content retrieval ([#46](https://github.com/koboriakira/sandpiper/issues/46)) ([5350fbe](https://github.com/koboriakira/sandpiper/commit/5350fbea448ced33b969c5cfe0571750c9776a4c))


### Bug Fixes

* Fix CI/CD pipeline failures ([#50](https://github.com/koboriakira/sandpiper/issues/50)) ([94ffa7f](https://github.com/koboriakira/sandpiper/commit/94ffa7f114fe9bb85d438313d0508e123fd67349))


### Documentation

* Update README and CLAUDE.md to reflect new features and project structure ([#49](https://github.com/koboriakira/sandpiper/issues/49)) ([454d5a5](https://github.com/koboriakira/sandpiper/commit/454d5a57180f0531577f48dceeceb7588f716a59))

## [0.8.0](https://github.com/koboriakira/sandpiper/compare/v0.7.0...v0.8.0) (2026-01-12)


### Features

* Add auto_fetch_title property for clips ([#42](https://github.com/koboriakira/sandpiper/issues/42)) ([ae668c6](https://github.com/koboriakira/sandpiper/commit/ae668c664d6934aab77487e2839fc6f61f50a96f))
* Add context property to someday list database ([#40](https://github.com/koboriakira/sandpiper/issues/40)) ([91984f1](https://github.com/koboriakira/sandpiper/commit/91984f10b0b13e83db6934be3881c493a76cce95))
* Add create-someday CLI command for adding someday list items ([#43](https://github.com/koboriakira/sandpiper/issues/43)) ([63571b7](https://github.com/koboriakira/sandpiper/commit/63571b75a87032b0340353386da3e7907a892a6d))

## [0.7.0](https://github.com/koboriakira/sandpiper/compare/v0.6.0...v0.7.0) (2026-01-12)


### Features

* Add archive endpoint for Notion deleted items ([#34](https://github.com/koboriakira/sandpiper/issues/34)) ([f92caf7](https://github.com/koboriakira/sandpiper/commit/f92caf7078b58615bbb5988f144aed1a6299b054))
* Add context property to Notion databases ([#35](https://github.com/koboriakira/sandpiper/issues/35)) ([067f13c](https://github.com/koboriakira/sandpiper/commit/067f13c7920cb9893238799d473289dfdccea72f))
* Add dish-related tasks to HandleCompletedTask ([#29](https://github.com/koboriakira/sandpiper/issues/29)) ([3a6de11](https://github.com/koboriakira/sandpiper/commit/3a6de1157a319df1a990192a35720ebbf9f572a3))
* Add inbox type detection for Notion clips API ([#37](https://github.com/koboriakira/sandpiper/issues/37)) ([277983e](https://github.com/koboriakira/sandpiper/commit/277983e348f4d7872cab6b2881da25f6fdfe3d62))
* Add JIRA ticket search and retrieval functionality ([#31](https://github.com/koboriakira/sandpiper/issues/31)) ([7085fc4](https://github.com/koboriakira/sandpiper/commit/7085fc4de6ab5b180dc4aaee41585876e5966305))
* Add Jira tickets to Notion projects ([#32](https://github.com/koboriakira/sandpiper/issues/32)) ([2ca4398](https://github.com/koboriakira/sandpiper/commit/2ca43981be60a8b806ad0f425314fe97d07f7fbc))
* Add POST /api/notion/clips endpoint for creating web clips ([#36](https://github.com/koboriakira/sandpiper/issues/36)) ([9a26828](https://github.com/koboriakira/sandpiper/commit/9a26828fd16c45d2628a953f990b4f35eef4c736))
* Create CLI command for Notion recipe pages ([#23](https://github.com/koboriakira/sandpiper/issues/23)) ([8fa1fcf](https://github.com/koboriakira/sandpiper/commit/8fa1fcf9da49b121be76cb7db4c93a157380c96f))
* Filter repeat task duplicates by "今日中にやる" property ([#26](https://github.com/koboriakira/sandpiper/issues/26)) ([c84cdba](https://github.com/koboriakira/sandpiper/commit/c84cdbaedf43f19f0f97844566a7da934a0af36f))
* Make clip title optional and auto-fetch from URL ([#38](https://github.com/koboriakira/sandpiper/issues/38)) ([c9bd716](https://github.com/koboriakira/sandpiper/commit/c9bd716e7aaaeef777b72b96285429d58b2e0736))
* Set up Notion database management for SomeDay list ([#27](https://github.com/koboriakira/sandpiper/issues/27)) ([31fb82e](https://github.com/koboriakira/sandpiper/commit/31fb82ebc74e079497cf28d80c19db210a817e70))
* Update CalendarEventPage to use date range for event start and end dates ([#30](https://github.com/koboriakira/sandpiper/issues/30)) ([093640c](https://github.com/koboriakira/sandpiper/commit/093640c8bce30f2de71cb7e851f333ee5f051f6f))


### Bug Fixes

* Update DATABASE_ID to the actual Notion Clips Database ID ([#39](https://github.com/koboriakira/sandpiper/issues/39)) ([243ef6a](https://github.com/koboriakira/sandpiper/commit/243ef6a2c31b131fac36a0d89f0bf7bc5691ba58))
* Upgrade urllib3 to 2.6.3 to fix CVE-2026-21441 ([#28](https://github.com/koboriakira/sandpiper/issues/28)) ([ab63f21](https://github.com/koboriakira/sandpiper/commit/ab63f2120b07d59a9e2b5f03116e7a03d749fbd2))

## [0.6.0](https://github.com/koboriakira/sandpiper/compare/v0.5.0...v0.6.0) (2026-01-07)


### Features

* Add date filtering for completed todos ([#19](https://github.com/koboriakira/sandpiper/issues/19)) ([dcf8f46](https://github.com/koboriakira/sandpiper/commit/dcf8f4606c59adaa6c0cbaa335d1809aa3b6d1b3))
* add response logging middleware to log response details ([5183723](https://github.com/koboriakira/sandpiper/commit/5183723592560ce566dc42a67350d0dc664e8e36))
* Copy block content when creating repeat tasks ([#22](https://github.com/koboriakira/sandpiper/issues/22)) ([08c23d3](https://github.com/koboriakira/sandpiper/commit/08c23d38e0f937c0350280098186088f736435ca))
* Copy execution time when creating repeat tasks ([#21](https://github.com/koboriakira/sandpiper/issues/21)) ([558d3df](https://github.com/koboriakira/sandpiper/commit/558d3dfdbcc8e323ae9193e241e81ea55e31fb2a))
* Create recipe context and add recipes ([#20](https://github.com/koboriakira/sandpiper/issues/20)) ([005ee2e](https://github.com/koboriakira/sandpiper/commit/005ee2e56864a6e7831f650123f74b23d5f678e6))

## [0.5.0](https://github.com/koboriakira/sandpiper/compare/v0.4.0...v0.5.0) (2026-01-06)


### Features

* Add convert TODO to project feature ([#13](https://github.com/koboriakira/sandpiper/issues/13)) ([2f4414b](https://github.com/koboriakira/sandpiper/commit/2f4414ba442e75baca7eac32dbdac3aef220c2b4))
* add endpoint to convert Todo to Project and update version to 0.3.0 ([ee20da1](https://github.com/koboriakira/sandpiper/commit/ee20da1bf58be75826c7d33c868fc97b9dd65965))
* add special todo handler endpoint for name-based processing ([#14](https://github.com/koboriakira/sandpiper/issues/14)) ([b323af6](https://github.com/koboriakira/sandpiper/commit/b323af6131207bd9b68cf38ccf96ed4727c0b435))
* Update project task status to in progress ([#16](https://github.com/koboriakira/sandpiper/issues/16)) ([64c68aa](https://github.com/koboriakira/sandpiper/commit/64c68aa3dad62d00ec2b6549b8acfd25c3d357ed))


### Bug Fixes

* rename unused test parameter to satisfy ruff ARG002 ([#15](https://github.com/koboriakira/sandpiper/issues/15)) ([3dac3ea](https://github.com/koboriakira/sandpiper/commit/3dac3eaa28b4a591ada4058ec0e7280f776827b8))
* TODOリスト作成の時刻ロジックを改善しルーチンタスクも追加 ([#17](https://github.com/koboriakira/sandpiper/issues/17)) ([3cff0cb](https://github.com/koboriakira/sandpiper/commit/3cff0cbab34a20c5845f24e3a5893316afd251c4))
* update logic to process routine tasks only if the date is today or earlier ([2991321](https://github.com/koboriakira/sandpiper/commit/2991321a870e1ec2ecf66141bf709c01a1e48e6b))
* update routine processing logic to skip tasks with future dates and improve logging ([22eb3ec](https://github.com/koboriakira/sandpiper/commit/22eb3ec170802c588117e70960fd5b6e6bf4fcab))

## [0.4.0](https://github.com/koboriakira/sandpiper/compare/v0.3.0...v0.4.0) (2026-01-05)


### Features

* add maintenance router and integrate with FastAPI application ([0ef46c2](https://github.com/koboriakira/sandpiper/commit/0ef46c291aeefab6cd63582bf5f5d79c1d47993e))
* プロジェクトタスクのデータベース操作 ([#11](https://github.com/koboriakira/sandpiper/issues/11)) ([ff05907](https://github.com/koboriakira/sandpiper/commit/ff059070b92fc41ac155a153d45057337fea7a22))
* プロジェクトデータベースの更新をする ([#9](https://github.com/koboriakira/sandpiper/issues/9)) ([7410771](https://github.com/koboriakira/sandpiper/commit/7410771df888a004d0106d233e52f6460728537e))

## [0.3.0](https://github.com/koboriakira/sandpiper/compare/v0.2.0...v0.3.0) (2026-01-05)


### Features

* カレンダー削除APIエンドポイント実装 ([#5](https://github.com/koboriakira/sandpiper/issues/5)) ([fb69391](https://github.com/koboriakira/sandpiper/commit/fb69391cd8bac2be43c08ed5aefcc53824466576))


### Bug Fixes

* improve event deletion logic and refactor category assignment ([ed81985](https://github.com/koboriakira/sandpiper/commit/ed819853d7e76aaea16ecaea41432977ae33e59f))

## [0.2.0](https://github.com/koboriakira/sandpiper/compare/v0.1.0...v0.2.0) (2026-01-05)


### Features

* calendar domain implementation with Notion integration ([#4](https://github.com/koboriakira/sandpiper/issues/4)) ([f415173](https://github.com/koboriakira/sandpiper/commit/f4151737586604a8a99bb6759458a60e39a3122c))
* GitHub活動ログ取得機能の追加 ([#2](https://github.com/koboriakira/sandpiper/issues/2)) ([9feef32](https://github.com/koboriakira/sandpiper/commit/9feef32a887a040b3bda3e42e02a84cb768173eb))

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

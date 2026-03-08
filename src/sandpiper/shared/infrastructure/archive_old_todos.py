"""完了して一定期間経過したTODOをアーカイブするサービス"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta

from lotion import BasePage, Lotion, notion_database

from sandpiper.shared.notion.databases import todo as todo_db
from sandpiper.shared.notion.databases import todo_archive as todo_archive_db
from sandpiper.shared.notion.databases.todo_archive import (
    TodoArchiveContext,
    TodoArchiveExecutionTime,
    TodoArchiveIsDeleted,
    TodoArchiveIsTodayProp,
    TodoArchiveKindProp,
    TodoArchiveLogDate,
    TodoArchiveName,
    TodoArchiveProjectProp,
    TodoArchiveProjectTaskProp,
    TodoArchiveSection,
    TodoArchiveSortOrder,
    TodoArchiveStatus,
)
from sandpiper.shared.utils.date_utils import jst_today_datetime
from sandpiper.shared.valueobject.todo_kind import ToDoKind
from sandpiper.shared.valueobject.todo_status_enum import ToDoStatusEnum

DEFAULT_ARCHIVE_DAYS = 1


@notion_database(todo_archive_db.DATABASE_ID)
class TodoArchivePage(BasePage):
    name: TodoArchiveName
    status: TodoArchiveStatus


@dataclass
class ArchiveOldTodosResult:
    """アーカイブ結果"""

    archived_count: int
    archived_titles: list[str]
    deleted_routine_count: int = 0
    deleted_routine_titles: list[str] = field(default_factory=list)


class ArchiveOldTodos:
    """完了して一定期間経過したTODOをアーカイブするサービス

    DONEステータスのTODOで、完了日時が閾値より古いものを処理します。
    - リピート(ルーティン)種別: アーカイブせず削除のみ
    - それ以外: アーカイブデータベースに移動後、元DBから削除
    """

    def __init__(
        self,
        archive_days: int = DEFAULT_ARCHIVE_DAYS,
    ) -> None:
        self.client = Lotion.get_instance()
        self.archive_days = archive_days

    def execute(self, dry_run: bool = False) -> ArchiveOldTodosResult:
        """完了して一定期間経過したTODOをアーカイブまたは削除する

        Args:
            dry_run: Trueの場合、実際の処理は行わず対象のみを返す

        Returns:
            ArchiveOldTodosResult: 処理されたTODOの件数とタイトル一覧
        """
        # 本日0時を基準に (archive_days - 1) 日前を閾値とする
        # archive_days=1 → 本日0時 = 前日以前のものが対象
        threshold_date = jst_today_datetime() - timedelta(days=self.archive_days - 1)

        pages = self.client.retrieve_database(todo_db.DATABASE_ID)

        archived_count = 0
        archived_titles: list[str] = []
        deleted_routine_count = 0
        deleted_routine_titles: list[str] = []

        for page in pages:
            if not self._should_process(page, threshold_date):
                continue

            title = page.get_title_text()
            is_routine = self._is_routine(page)

            if not dry_run:
                if not is_routine:
                    self._archive_page(page)
                self.client.remove_page(page.id)

            if is_routine:
                deleted_routine_count += 1
                deleted_routine_titles.append(title)
            else:
                archived_count += 1
                archived_titles.append(title)

        return ArchiveOldTodosResult(
            archived_count=archived_count,
            archived_titles=archived_titles,
            deleted_routine_count=deleted_routine_count,
            deleted_routine_titles=deleted_routine_titles,
        )

    def _should_process(self, page: BasePage, threshold_date: datetime) -> bool:
        """ページが処理対象かどうかを判定"""
        status = ToDoStatusEnum(page.get_status("ステータス").status_name)
        if status != ToDoStatusEnum.DONE:
            return False

        perform_range = page.get_date("実施期間")
        if perform_range.end is None:
            return False

        end_datetime = datetime.fromisoformat(perform_range.end)
        return end_datetime < threshold_date

    def _is_routine(self, page: BasePage) -> bool:
        """リピート(ルーティン)種別かどうかを判定"""
        kind = page.get_select("タスク種別")
        return kind.selected_name == ToDoKind.REPEAT.value

    def _archive_page(self, page: BasePage) -> None:
        """ページをアーカイブデータベースにコピー"""
        properties = [
            TodoArchiveName.from_plain_text(page.get_title_text()),
            TodoArchiveStatus.from_status_name(page.get_status("ステータス").status_name),
        ]

        section = page.get_select("セクション")
        if section.selected_name:
            properties.append(TodoArchiveSection.from_name(section.selected_name))

        is_today = page.get_checkbox("今日中にやる")
        properties.append(TodoArchiveIsTodayProp.true() if is_today.checked else TodoArchiveIsTodayProp.false())

        perform_range = page.get_date("実施期間")
        if perform_range.start or perform_range.end:
            start_dt = datetime.fromisoformat(perform_range.start) if perform_range.start else None
            end_dt = datetime.fromisoformat(perform_range.end) if perform_range.end else None
            properties.append(TodoArchiveLogDate.from_range(start=start_dt, end=end_dt))

        kind = page.get_select("タスク種別")
        if kind.selected_name:
            properties.append(TodoArchiveKindProp.from_name(kind.selected_name))

        project = page.get_relation("プロジェクト")
        if project.id_list:
            properties.append(TodoArchiveProjectProp.from_id(project.id_list[0]))

        project_task = page.get_relation("プロジェクトタスク")
        if project_task.id_list:
            properties.append(TodoArchiveProjectTaskProp.from_id(project_task.id_list[0]))

        execution_time = page.get_number("実行時間")
        if execution_time.number is not None:
            properties.append(TodoArchiveExecutionTime.from_num(int(execution_time.number)))

        is_deleted = page.get_checkbox("論理削除")
        properties.append(TodoArchiveIsDeleted.true() if is_deleted.checked else TodoArchiveIsDeleted.false())

        context = page.get_multi_select("コンテクスト")
        if context.values:
            context_names = [v.name for v in context.values]
            properties.append(TodoArchiveContext.from_name(context_names))

        sort_order = page.get_text("並び順")
        if sort_order.text:
            properties.append(TodoArchiveSortOrder.from_plain_text(sort_order.text))

        archive_page = TodoArchivePage.create(properties=properties)
        self.client.create_page(archive_page)

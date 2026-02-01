"""予定開始時刻からセクションを上書きするユースケース"""

from dataclasses import dataclass
from datetime import timedelta

from sandpiper.perform.domain.todo_repository import TodoRepository
from sandpiper.shared.valueobject.task_chute_section import TaskChuteSection

# JSTオフセット
JST_OFFSET = timedelta(hours=9)


@dataclass
class OverrideSectionResult:
    """セクション上書き結果"""

    page_id: str
    title: str
    old_section: TaskChuteSection | None
    new_section: TaskChuteSection
    scheduled_start_datetime_str: str


class OverrideSectionBySchedule:
    """予定開始時刻からセクションを上書きする"""

    def __init__(self, todo_repository: TodoRepository) -> None:
        self._todo_repository = todo_repository

    def execute(self, page_id: str) -> OverrideSectionResult:
        """
        指定されたTODOの予定開始時刻からセクションを計算し、上書きする

        Args:
            page_id: TODOのページID

        Returns:
            OverrideSectionResult: 上書き結果

        Raises:
            ValueError: 予定開始日時が設定されていない場合
        """
        todo = self._todo_repository.find(page_id)

        if todo.scheduled_start_datetime is None:
            msg = f"予定開始日時が設定されていません: {todo.title}"
            raise ValueError(msg)

        # JSTに変換
        scheduled_jst = todo.scheduled_start_datetime
        if scheduled_jst.tzinfo is None:
            # naive datetimeの場合はUTCとみなしてJSTに変換
            scheduled_jst = scheduled_jst + JST_OFFSET

        # セクションを計算
        new_section = TaskChuteSection.new(scheduled_jst)

        # セクションを上書き
        self._todo_repository.update_section(page_id, new_section)

        return OverrideSectionResult(
            page_id=page_id,
            title=todo.title,
            old_section=todo.section,
            new_section=new_section,
            scheduled_start_datetime_str=scheduled_jst.strftime("%Y-%m-%d %H:%M"),
        )

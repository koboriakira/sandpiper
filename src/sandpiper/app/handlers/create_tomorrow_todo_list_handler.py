"""明日のTODOリスト作成ハンドラー

「明日のTODOリストを作成」というタイトルのTODOに対して、
プロジェクトタスクから明日のTODOリストを自動生成します。

日本時間の18:00〜23:59に実行された場合は「明日」のTODOとして作成し、
00:00〜17:59に実行された場合は「今日」のTODOとして作成します。
"""

from datetime import date, datetime
from zoneinfo import ZoneInfo

from sandpiper.app.handlers.special_todo_handler import (
    HandleSpecialTodoResult,
    SpecialTodoHandler,
)
from sandpiper.plan.application.create_repeat_project_task import CreateRepeatProjectTask
from sandpiper.plan.application.create_repeat_task import CreateRepeatTask

JST = ZoneInfo("Asia/Tokyo")


def _should_create_for_tomorrow() -> bool:
    """日本時間の現在時刻から、明日のTODOを作成すべきかを判定する

    18:00〜23:59の場合は明日のTODO、それ以外は今日のTODOを作成する

    Returns:
        bool: 明日のTODOを作成すべき場合True
    """
    now_jst = datetime.now(JST)
    return 18 <= now_jst.hour <= 23


def _get_basis_date() -> date:
    """CreateRepeatTask用の基準日を取得する

    18:00〜23:59の場合は明日の日付、それ以外は今日の日付を返す

    Returns:
        date: 基準日
    """
    now_jst = datetime.now(JST)
    if 18 <= now_jst.hour <= 23:
        # 明日の日付を返す
        from datetime import timedelta

        return (now_jst + timedelta(days=1)).date()
    return now_jst.date()


class CreateTomorrowTodoListHandler(SpecialTodoHandler):
    """明日のTODOリストを作成するハンドラー

    「明日のTODOリストを作成」というタイトルのTODOが処理されると、
    CreateRepeatProjectTaskとCreateRepeatTaskユースケースを実行して、
    プロジェクトタスクとルーチンタスクからTODOを自動生成します。

    日本時間18:00〜23:59は明日のTODO、00:00〜17:59は今日のTODOとして作成します。
    """

    TARGET_TITLE = "明日のTODOリストを作成"

    def __init__(
        self,
        create_repeat_project_task: CreateRepeatProjectTask,
        create_repeat_task: CreateRepeatTask,
    ) -> None:
        """初期化

        Args:
            create_repeat_project_task: プロジェクトタスクからTODOを作成するユースケース
            create_repeat_task: ルーチンタスクからTODOを作成するユースケース
        """
        self._create_repeat_project_task = create_repeat_project_task
        self._create_repeat_task = create_repeat_task

    @property
    def handler_name(self) -> str:
        return "create_tomorrow_todo_list"

    @property
    def target_title(self) -> str:
        return self.TARGET_TITLE

    def handle(self, page_id: str, title: str) -> HandleSpecialTodoResult:
        """TODOリストを作成する

        日本時間18:00〜23:59は明日のTODO、00:00〜17:59は今日のTODOとして作成。
        プロジェクトタスクとルーチンタスクの両方を処理します。

        Args:
            page_id: NotionのページID
            title: TODOのタイトル

        Returns:
            HandleSpecialTodoResult: 処理結果
        """
        try:
            is_tomorrow = _should_create_for_tomorrow()
            basis_date = _get_basis_date()
            target_day = "明日" if is_tomorrow else "今日"

            # プロジェクトタスクからTODOを作成
            self._create_repeat_project_task.execute(is_tomorrow=is_tomorrow)

            # ルーチンタスクからTODOを作成
            self._create_repeat_task.execute(basis_date=basis_date)

            return self._success_result(
                page_id=page_id,
                title=title,
                message=f"{target_day}のTODOリストを作成しました",
            )
        except Exception as e:
            return self._failure_result(
                page_id=page_id,
                title=title,
                message=f"TODOリスト作成に失敗しました: {e}",
            )

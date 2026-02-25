"""明日のTODOリスト作成ハンドラー

「明日のTODOリストを作成」というタイトルのTODOに対して、
プロジェクトタスクから明日のTODOリストを自動生成します。

日本時間の18:00〜23:59に実行された場合は「明日」のTODOとして作成し、
00:00〜17:59に実行された場合は「今日」のTODOとして作成します。
"""

from datetime import datetime
from zoneinfo import ZoneInfo

from sandpiper.app.handlers.special_todo_handler import (
    HandleSpecialTodoResult,
    SpecialTodoHandler,
)
from sandpiper.plan.application.prepare_tomorrow_todos import PrepareTomorrowTodos

JST = ZoneInfo("Asia/Tokyo")


class CreateTomorrowTodoListHandler(SpecialTodoHandler):
    """明日のTODOリストを作成するハンドラー

    「明日のTODOリストを作成」というタイトルのTODOが処理されると、
    PrepareTomorrowTodosユースケースを実行して、
    プロジェクトタスクとルーチンタスクからTODOを自動生成します。

    日本時間18:00〜23:59は明日のTODO、00:00〜17:59は今日のTODOとして作成します。
    """

    TARGET_TITLE = "明日のTODOリストを作成"

    def __init__(
        self,
        prepare_tomorrow_todos: PrepareTomorrowTodos,
    ) -> None:
        self._prepare_tomorrow_todos = prepare_tomorrow_todos

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
            now_jst = datetime.now(JST)
            is_tomorrow, basis_date = PrepareTomorrowTodos.resolve_params_from_now(
                now_hour=now_jst.hour, today=now_jst.date()
            )

            result = self._prepare_tomorrow_todos.execute(is_tomorrow=is_tomorrow, basis_date=basis_date)

            return self._success_result(
                page_id=page_id,
                title=title,
                message=result.summary,
            )
        except Exception as e:
            return self._failure_result(
                page_id=page_id,
                title=title,
                message=f"TODOリスト作成に失敗しました: {e}",
            )

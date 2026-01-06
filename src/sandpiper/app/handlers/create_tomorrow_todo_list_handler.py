"""明日のTODOリスト作成ハンドラー

「明日のTODOリストを作成」というタイトルのTODOに対して、
プロジェクトタスクから明日のTODOリストを自動生成します。
"""

from sandpiper.app.handlers.special_todo_handler import (
    HandleSpecialTodoResult,
    SpecialTodoHandler,
)
from sandpiper.plan.application.create_repeat_project_task import CreateRepeatProjectTask


class CreateTomorrowTodoListHandler(SpecialTodoHandler):
    """明日のTODOリストを作成するハンドラー

    「明日のTODOリストを作成」というタイトルのTODOが処理されると、
    CreateRepeatProjectTaskユースケースを実行して、
    プロジェクトタスクから明日のTODOを自動生成します。
    """

    TARGET_TITLE = "明日のTODOリストを作成"

    def __init__(self, create_repeat_project_task: CreateRepeatProjectTask) -> None:
        """初期化

        Args:
            create_repeat_project_task: プロジェクトタスクからTODOを作成するユースケース
        """
        self._create_repeat_project_task = create_repeat_project_task

    @property
    def handler_name(self) -> str:
        return "create_tomorrow_todo_list"

    @property
    def target_title(self) -> str:
        return self.TARGET_TITLE

    def handle(self, page_id: str, title: str) -> HandleSpecialTodoResult:
        """明日のTODOリストを作成する

        Args:
            page_id: NotionのページID
            title: TODOのタイトル

        Returns:
            HandleSpecialTodoResult: 処理結果
        """
        try:
            self._create_repeat_project_task.execute(is_tomorrow=True)
            return self._success_result(
                page_id=page_id,
                title=title,
                message="明日のTODOリストを作成しました",
            )
        except Exception as e:
            return self._failure_result(
                page_id=page_id,
                title=title,
                message=f"明日のTODOリスト作成に失敗しました: {e}",
            )

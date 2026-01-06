"""特定の名前のTODOに対して特殊処理を実行するユースケース"""

from abc import ABC, abstractmethod
from dataclasses import dataclass

from sandpiper.perform.domain.todo_repository import TodoRepository


@dataclass
class HandleSpecialTodoResult:
    """特殊処理の結果"""

    page_id: str
    title: str
    handler_name: str
    success: bool
    message: str


class SpecialTodoHandler(ABC):
    """特定のTODO名に対するハンドラーの基底クラス"""

    @property
    @abstractmethod
    def target_title(self) -> str:
        """処理対象のTODO名"""
        ...

    @abstractmethod
    def handle(self, page_id: str, title: str) -> HandleSpecialTodoResult:
        """特殊処理を実行する"""
        ...


class HandleSpecialTodo:
    """特定の名前のTODOに対して特殊処理を実行する

    TODOのタイトルに基づいて、登録されたハンドラーを実行します。
    新しい特殊処理を追加する場合は、SpecialTodoHandlerを継承したクラスを作成し、
    register_handlerメソッドで登録してください。
    """

    def __init__(self, todo_repository: TodoRepository) -> None:
        self._todo_repository = todo_repository
        self._handlers: dict[str, SpecialTodoHandler] = {}

    def register_handler(self, handler: SpecialTodoHandler) -> None:
        """ハンドラーを登録する

        Args:
            handler: 登録するハンドラー
        """
        self._handlers[handler.target_title] = handler

    def get_registered_titles(self) -> list[str]:
        """登録されているハンドラーのタイトル一覧を取得する"""
        return list(self._handlers.keys())

    def execute(self, page_id: str) -> HandleSpecialTodoResult:
        """特殊処理を実行する

        Args:
            page_id: NotionのページID

        Returns:
            HandleSpecialTodoResult: 処理結果
        """
        todo = self._todo_repository.find(page_id)
        title = todo.title

        handler = self._handlers.get(title)
        if handler is None:
            return HandleSpecialTodoResult(
                page_id=page_id,
                title=title,
                handler_name="none",
                success=False,
                message=f"No handler registered for title: {title}",
            )

        return handler.handle(page_id, title)

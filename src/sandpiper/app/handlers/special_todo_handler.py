"""特殊TODOハンドラーの基底クラスと結果型

このモジュールはドメイン横断的なハンドラーの抽象化を提供します。
各ハンドラーは特定のTODOタイトルに対して、必要なユースケースを
組み合わせた処理を実行します。
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class HandleSpecialTodoResult:
    """特殊処理の結果"""

    page_id: str
    title: str
    handler_name: str
    success: bool
    message: str


class SpecialTodoHandler(ABC):
    """特定のTODO名に対するハンドラーの基底クラス

    各ハンドラーは特定のTODOタイトルに反応し、
    必要なユースケースを組み合わせて処理を実行します。

    ハンドラーはアプリケーション層に属し、複数のドメインサービスや
    ユースケースを組み合わせたオーケストレーションを担当します。
    """

    @property
    @abstractmethod
    def handler_name(self) -> str:
        """ハンドラーの識別名"""
        ...

    @property
    @abstractmethod
    def target_title(self) -> str:
        """処理対象のTODO名"""
        ...

    @abstractmethod
    def handle(self, page_id: str, title: str) -> HandleSpecialTodoResult:
        """特殊処理を実行する

        Args:
            page_id: NotionのページID
            title: TODOのタイトル

        Returns:
            HandleSpecialTodoResult: 処理結果
        """
        ...

    def _success_result(self, page_id: str, title: str, message: str) -> HandleSpecialTodoResult:
        """成功結果を生成するヘルパーメソッド"""
        return HandleSpecialTodoResult(
            page_id=page_id,
            title=title,
            handler_name=self.handler_name,
            success=True,
            message=message,
        )

    def _failure_result(self, page_id: str, title: str, message: str) -> HandleSpecialTodoResult:
        """失敗結果を生成するヘルパーメソッド"""
        return HandleSpecialTodoResult(
            page_id=page_id,
            title=title,
            handler_name=self.handler_name,
            success=False,
            message=message,
        )

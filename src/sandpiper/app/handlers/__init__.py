"""ドメイン横断的なハンドラーモジュール

このモジュールには、複数のドメインにまたがる処理を調整するハンドラーが含まれます。
DDDのアプリケーション層として、ドメインサービスやユースケースを組み合わせた
オーケストレーションを担当します。
"""

from sandpiper.app.handlers.special_todo_handler import (
    HandleSpecialTodoResult,
    SpecialTodoHandler,
)

__all__ = [
    "HandleSpecialTodoResult",
    "SpecialTodoHandler",
]

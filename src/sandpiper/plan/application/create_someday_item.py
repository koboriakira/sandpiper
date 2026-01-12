"""サムデイリストにアイテムを追加するユースケース"""

from dataclasses import dataclass

from sandpiper.plan.domain.someday_item import SomedayItem, SomedayTiming
from sandpiper.plan.domain.someday_repository import SomedayRepository


@dataclass
class CreateSomedayItemRequest:
    """サムデイアイテム作成リクエスト"""

    title: str


@dataclass
class CreateSomedayItemResult:
    """サムデイアイテム作成結果"""

    id: str
    title: str
    timing: str


class CreateSomedayItem:
    """サムデイリストにアイテムを追加するユースケース

    タイミングは必ず「明日」が設定されます。
    """

    def __init__(self, someday_repository: SomedayRepository) -> None:
        self.someday_repository = someday_repository

    def execute(self, request: CreateSomedayItemRequest) -> CreateSomedayItemResult:
        """サムデイアイテムを作成する

        Args:
            request: サムデイアイテム作成リクエスト

        Returns:
            作成されたサムデイアイテムの情報
        """
        item = SomedayItem.create(
            title=request.title,
            timing=SomedayTiming.TOMORROW,
        )
        saved_item = self.someday_repository.save(item)

        return CreateSomedayItemResult(
            id=saved_item.id,
            title=saved_item.title,
            timing=saved_item.timing.value,
        )

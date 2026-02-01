"""サムデイリストにアイテムを追加するユースケース"""

from dataclasses import dataclass, field

from sandpiper.plan.domain.someday_item import SomedayItem, SomedayTiming
from sandpiper.plan.domain.someday_repository import SomedayRepository


@dataclass
class CreateSomedayItemRequest:
    """サムデイアイテム作成リクエスト"""

    title: str
    timing: SomedayTiming = SomedayTiming.TOMORROW
    do_tomorrow: bool = False
    context: list[str] = field(default_factory=list)


@dataclass
class CreateSomedayItemResult:
    """サムデイアイテム作成結果"""

    id: str
    title: str
    timing: str
    do_tomorrow: bool
    context: list[str]


class CreateSomedayItem:
    """サムデイリストにアイテムを追加するユースケース

    デフォルトではタイミングが「明日」に設定されます。
    オプションでタイミング、明日やるフラグ、コンテクストを指定できます。
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
            timing=request.timing,
            do_tomorrow=request.do_tomorrow,
            context=request.context,
        )
        saved_item = self.someday_repository.save(item)

        return CreateSomedayItemResult(
            id=saved_item.id,
            title=saved_item.title,
            timing=saved_item.timing.value,
            do_tomorrow=saved_item.do_tomorrow,
            context=saved_item.context,
        )

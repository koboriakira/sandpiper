from dataclasses import dataclass, field
from enum import Enum


class SomedayTiming(Enum):
    """サムデイリストのタイミング"""

    TOMORROW = "明日"
    SOMEDAY = "いつか"


@dataclass
class SomedayItem:
    """サムデイリストのアイテム"""

    id: str
    title: str
    timing: SomedayTiming
    do_tomorrow: bool = False
    is_deleted: bool = False
    context: list[str] = field(default_factory=list)

    @classmethod
    def create(
        cls,
        title: str,
        timing: SomedayTiming = SomedayTiming.SOMEDAY,
        do_tomorrow: bool = False,
        context: list[str] | None = None,
    ) -> "SomedayItem":
        """新しいサムデイアイテムを作成"""
        return cls(
            id="",
            title=title,
            timing=timing,
            do_tomorrow=do_tomorrow,
            is_deleted=False,
            context=context or [],
        )

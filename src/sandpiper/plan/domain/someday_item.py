from dataclasses import dataclass
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

    @classmethod
    def create(
        cls,
        title: str,
        timing: SomedayTiming = SomedayTiming.SOMEDAY,
        do_tomorrow: bool = False,
    ) -> "SomedayItem":
        """新しいサムデイアイテムを作成"""
        return cls(
            id="",
            title=title,
            timing=timing,
            do_tomorrow=do_tomorrow,
            is_deleted=False,
        )

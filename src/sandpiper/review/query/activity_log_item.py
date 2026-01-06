from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class ActivityType(Enum):
    """アクティビティの種別"""

    TODO = "TODO"
    CALENDAR = "CALENDAR"


@dataclass
class ActivityLogItem:
    """TODOとカレンダーイベントを統合したログアイテム"""

    activity_type: ActivityType
    title: str
    start_datetime: datetime
    end_datetime: datetime
    # TODO固有のフィールド
    kind: str = ""  # ToDoKind.value
    project_name: str = ""
    # カレンダー固有のフィールド
    category: str = ""  # EventCategory.value

    @property
    def duration_minutes(self) -> int:
        """実施時間(分)を返す"""
        delta = self.end_datetime - self.start_datetime
        return int(delta.total_seconds() / 60)

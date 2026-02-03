from dataclasses import dataclass
from datetime import datetime, timedelta

from sandpiper.shared.valueobject.context import Context


@dataclass
class TodoStarted:
    name: str
    execution_time: datetime
    context: Context | None = None
    scheduled_duration: timedelta | None = None

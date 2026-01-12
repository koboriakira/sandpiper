from dataclasses import dataclass
from datetime import datetime

from sandpiper.shared.valueobject.context import Context


@dataclass
class TodoStartEvent:
    name: str
    context: Context
    execution_time: datetime

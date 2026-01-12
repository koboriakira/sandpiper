from dataclasses import dataclass
from datetime import datetime


@dataclass
class TodoStartEvent:
    name: str
    context: str
    execution_time: datetime

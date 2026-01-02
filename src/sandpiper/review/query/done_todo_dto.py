from dataclasses import dataclass
from datetime import datetime

from sandpiper.plan.domain.todo import ToDoKind


@dataclass
class DoneTodoDto:
    page_id: str
    title: str
    perform_range: tuple[datetime, datetime]
    kind: ToDoKind

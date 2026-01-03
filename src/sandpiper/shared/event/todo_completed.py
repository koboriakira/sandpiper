from dataclasses import dataclass


@dataclass
class TodoCompleted:
    page_id: str
    title: str

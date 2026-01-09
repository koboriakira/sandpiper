from dataclasses import dataclass
from datetime import date


@dataclass
class Project:
    """プロジェクトエンティティ"""

    name: str
    start_date: date
    end_date: date | None = None
    jira_url: str | None = None


@dataclass
class InsertedProject:
    """保存されたプロジェクトエンティティ"""

    id: str
    name: str
    start_date: date
    end_date: date | None = None
    jira_url: str | None = None

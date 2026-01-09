from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class JiraTicketDto:
    issue_key: str
    summary: str
    issue_type: str
    status: str
    priority: str | None = None
    assignee: str | None = None
    reporter: str | None = None
    created: datetime | None = None
    updated: datetime | None = None
    due_date: datetime | None = None
    description: str | None = None
    labels: list[str] | None = None
    fix_versions: list[str] | None = None
    components: list[str] | None = None
    sprint: str | None = None
    story_points: float | None = None
    epic_key: str | None = None
    parent_key: str | None = None
    github_issue: str | None = None
    url: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "issue_key": self.issue_key,
            "summary": self.summary,
            "issue_type": self.issue_type,
            "status": self.status,
            "priority": self.priority,
            "assignee": self.assignee,
            "reporter": self.reporter,
            "created": self.created.isoformat() if self.created else None,
            "updated": self.updated.isoformat() if self.updated else None,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "description": self.description,
            "labels": self.labels,
            "fix_versions": self.fix_versions,
            "components": self.components,
            "sprint": self.sprint,
            "story_points": self.story_points,
            "epic_key": self.epic_key,
            "parent_key": self.parent_key,
            "github_issue": self.github_issue,
            "url": self.url,
        }

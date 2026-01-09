import os
from datetime import datetime
from typing import Protocol

import requests
from requests import Session

from sandpiper.plan.query.jira_ticket_dto import JiraTicketDto


class JiraTicketQuery(Protocol):
    def search_tickets(
        self,
        jql: str | None = None,
        project: str | None = None,
        issue_type: str | None = None,
        status: str | None = None,
        assignee: str | None = None,
        max_results: int = 50,
    ) -> list[JiraTicketDto]: ...

    def get_ticket(self, issue_key: str) -> JiraTicketDto | None: ...


class RestApiJiraTicketQuery(JiraTicketQuery):
    def __init__(self, base_url: str | None = None, username: str | None = None, api_token: str | None = None) -> None:
        self.base_url = base_url or os.getenv("BUSINESS_JIRA_BASE_URL")
        if not self.base_url:
            raise ValueError("BUSINESS_JIRA_BASE_URL must be set")

        username = username or os.getenv("BUSINESS_JIRA_USERNAME")
        api_token = api_token or os.getenv("BUSINESS_JIRA_API_TOKEN")

        if not username or not api_token:
            msg = "BUSINESS_JIRA_USERNAME and BUSINESS_JIRA_API_TOKEN must be set"
            raise ValueError(msg)

        self.session = Session()
        self.session.auth = (username, api_token)
        self.session.headers.update({"Accept": "application/json"})
        self.default_project = os.getenv("BUSINESS_JIRA_PROJECT")

    def search_tickets(
        self,
        jql: str | None = None,
        project: str | None = None,
        issue_type: str | None = None,
        status: str | None = None,
        assignee: str | None = None,
        max_results: int = 50,
    ) -> list[JiraTicketDto]:
        # Build JQL if not provided
        if not jql:
            jql = self._build_jql(project, issue_type, status, assignee)

        # Define fields to fetch (basic fields only)
        fields = [
            "summary",
            "issuetype",
            "status",
            "priority",
            "assignee",
            "reporter",
            "created",
            "updated",
        ]

        url = f"{self.base_url}/rest/api/3/search/jql"
        params = {
            "jql": jql,
            "maxResults": min(max_results, 100),  # JIRA限制
            "fields": "key,summary,issuetype,status,priority,assignee,reporter,created,updated",
        }
        next_page_token = None

        tickets = []
        total_fetched = 0

        while total_fetched < max_results:
            # Add pagination token if exists
            if next_page_token:
                params["startAt"] = next_page_token

            try:
                response = self.session.get(url, params=params)
                response.raise_for_status()
            except requests.HTTPError as e:
                # Include response body for debugging
                error_msg = f"{e}"
                if hasattr(e.response, "text"):
                    try:
                        error_data = e.response.json()
                        error_msg += f" - {error_data}"
                    except:
                        error_msg += f" - {e.response.text[:500]}"
                raise requests.HTTPError(error_msg, response=e.response)

            data = response.json()
            issues = data.get("issues", [])

            if not issues:
                break

            for issue in issues:
                ticket = self._parse_issue(issue)
                tickets.append(ticket)
                total_fetched += 1

                if total_fetched >= max_results:
                    break

            # Check if there are more results using new pagination system
            is_last = data.get("isLast", True)
            next_page_token = data.get("nextPageToken")

            if is_last or not next_page_token:
                break

        return tickets

    def get_ticket(self, issue_key: str) -> JiraTicketDto | None:
        url = f"{self.base_url}/rest/api/3/issue/{issue_key}"

        try:
            response = self.session.get(url)
            response.raise_for_status()
            data = response.json()
            return self._parse_issue(data)
        except requests.HTTPError as e:
            if e.response.status_code == 404:
                return None
            raise

    def _build_jql(
        self,
        project: str | None = None,
        issue_type: str | None = None,
        status: str | None = None,
        assignee: str | None = None,
    ) -> str:
        conditions = []

        if project:
            conditions.append(f'project = "{project}"')
        elif self.default_project:
            conditions.append(f'project = "{self.default_project}"')
        else:
            raise ValueError("Project must be specified either in argument or BUSINESS_JIRA_PROJECT env variable")

        if issue_type:
            if "," in issue_type:
                types = [f'"{t.strip()}"' for t in issue_type.split(",")]
                conditions.append(f"issuetype IN ({','.join(types)})")
            else:
                conditions.append(f'issuetype = "{issue_type}"')

        if status:
            if "," in status:
                statuses = [f'"{s.strip()}"' for s in status.split(",")]
                conditions.append(f"status IN ({','.join(statuses)})")
            else:
                conditions.append(f'status = "{status}"')

        if assignee:
            if assignee.lower() == "currentuser()":
                conditions.append("assignee = currentUser()")
            else:
                conditions.append(f'assignee = "{assignee}"')
        else:
            assignee = os.getenv("BUSINESS_JIRA_USERNAME")
            if assignee:
                conditions.append(f'assignee = "{assignee}"')

        return " AND ".join(conditions) if conditions else "ORDER BY created DESC"

    def _parse_issue(self, issue: dict) -> JiraTicketDto:
        fields = issue.get("fields", {})

        # Parse basic fields
        issue_key = issue.get("key", "")
        summary = fields.get("summary", "")
        issue_type = fields.get("issuetype", {}).get("name", "")
        status = fields.get("status", {}).get("name", "")
        priority = fields.get("priority", {}).get("name") if fields.get("priority") else None

        # Parse people
        assignee_field = fields.get("assignee")
        assignee = assignee_field.get("displayName") if assignee_field else None

        reporter_field = fields.get("reporter")
        reporter = reporter_field.get("displayName") if reporter_field else None

        # Parse dates
        created = self._parse_datetime(fields.get("created"))
        updated = self._parse_datetime(fields.get("updated"))
        due_date = None  # Not fetched in basic field set

        # Parse other fields (not fetched in basic field set)
        description = None
        labels = []
        fix_versions = []
        components = []

        # Parse custom fields (set to None for now since they may not exist)
        sprint = None
        story_points = None
        epic_key = None
        parent = fields.get("parent", {})
        parent_key = parent.get("key") if parent else None
        github_issue = None

        # Build URL
        url = f"{self.base_url}/browse/{issue_key}"

        return JiraTicketDto(
            issue_key=issue_key,
            summary=summary,
            issue_type=issue_type,
            status=status,
            priority=priority,
            assignee=assignee,
            reporter=reporter,
            created=created,
            updated=updated,
            due_date=due_date,
            description=description,
            labels=labels,
            fix_versions=fix_versions,
            components=components,
            sprint=sprint,
            story_points=story_points,
            epic_key=epic_key,
            parent_key=parent_key,
            github_issue=github_issue,
            url=url,
        )

    def _parse_datetime(self, date_str: str | None) -> datetime | None:
        if not date_str:
            return None
        try:
            # JIRA returns dates in ISO format with timezone
            # Example: "2024-01-15T10:30:45.000+0000"
            return datetime.fromisoformat(date_str.replace("Z", "+00:00").replace("+0000", "+00:00"))
        except (ValueError, AttributeError):
            return None


if __name__ == "__main__":
    # uv run python -m src.sandpiper.plan.query.jira_ticket_query
    jira_query = RestApiJiraTicketQuery()
    tickets = jira_query.search_tickets(status="To Do", max_results=5)
    for ticket in tickets:
        print(f"{ticket.issue_key}: {ticket.summary} - {ticket.status}")

from dataclasses import dataclass

from sandpiper.plan.domain.project import InsertedProject, Project
from sandpiper.plan.domain.project_repository import ProjectRepository
from sandpiper.plan.domain.project_task import ProjectTask
from sandpiper.plan.domain.project_task_repository import ProjectTaskRepository
from sandpiper.plan.query.jira_ticket_dto import JiraTicketDto
from sandpiper.plan.query.jira_ticket_query import JiraTicketQuery
from sandpiper.shared.utils.date_utils import jst_today
from sandpiper.shared.valueobject.todo_status_enum import ToDoStatusEnum


@dataclass
class SyncJiraToProjectResult:
    """JIRAチケットからプロジェクトへの同期結果"""

    created_projects: list[InsertedProject]
    skipped_tickets: list[JiraTicketDto]


class SyncJiraToProject:
    """JIRAチケットをNotionプロジェクトに同期するユースケース

    SUプロジェクトの自分にアサインされたTask/Story/Bugチケットを取得し、
    Notionプロジェクトデータベースに追加する。
    - ステータスが"In Progress"のチケットを対象
    - 既にJira URLが登録されているプロジェクトは作成しない(重複チェック)
    - プロジェクト作成時に同名のプロジェクトタスクも作成
    """

    def __init__(
        self,
        jira_ticket_query: JiraTicketQuery,
        project_repository: ProjectRepository,
        project_task_repository: ProjectTaskRepository,
    ) -> None:
        self._jira_ticket_query = jira_ticket_query
        self._project_repository = project_repository
        self._project_task_repository = project_task_repository

    def execute(self, jira_project: str = "SU") -> SyncJiraToProjectResult:
        """JIRAチケットをNotionプロジェクトに同期する

        Args:
            jira_project: JIRAプロジェクトキー(デフォルト: SU)

        Returns:
            SyncJiraToProjectResult: 作成されたプロジェクトとスキップされたチケットのリスト
        """
        # JIRAからチケットを取得
        tickets = self._jira_ticket_query.search_tickets(
            project=jira_project,
            issue_type="Task,Story,Bug",
            status="In Progress",
            assignee="currentUser()",
            max_results=100,
        )

        # 既存のJira URLを一括取得(API呼び出し最適化)
        existing_jira_urls = self._project_repository.fetch_all_jira_urls()

        created_projects: list[InsertedProject] = []
        skipped_tickets: list[JiraTicketDto] = []

        for ticket in tickets:
            # URLがない場合はスキップ
            if not ticket.url:
                skipped_tickets.append(ticket)
                continue

            # URLで重複チェック(メモリ内で実行)
            if ticket.url in existing_jira_urls:
                skipped_tickets.append(ticket)
                continue

            # プロジェクト名はJIRAチケットのsummary
            project = Project(
                name=ticket.summary,
                start_date=jst_today(),
                jira_url=ticket.url,
            )
            inserted_project = self._project_repository.save(project)
            created_projects.append(inserted_project)

            # 新規作成したURLを追加(同一実行内での重複防止)
            existing_jira_urls.add(ticket.url)

            # 同名のプロジェクトタスクを作成
            project_task = ProjectTask(
                title=ticket.summary,
                status=ToDoStatusEnum.TODO,
                project_id=inserted_project.id,
            )
            self._project_task_repository.save(project_task)

        return SyncJiraToProjectResult(
            created_projects=created_projects,
            skipped_tickets=skipped_tickets,
        )

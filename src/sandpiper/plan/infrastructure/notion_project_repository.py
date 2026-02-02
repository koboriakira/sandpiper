from lotion import BasePage, Lotion, notion_database
from lotion.filter import Builder, Cond

from sandpiper.plan.domain.project import InsertedProject, Project
from sandpiper.shared.notion.databases import project as project_db
from sandpiper.shared.notion.databases.project import (
    ProjectEndDate,
    ProjectJiraUrl,
    ProjectName,
    ProjectStartDate,
    ProjectStatus,
)
from sandpiper.shared.valueobject.todo_status_enum import ToDoStatusEnum


@notion_database(project_db.DATABASE_ID)
class ProjectPage(BasePage):  # type: ignore[misc]
    name: ProjectName
    start_date: ProjectStartDate
    end_date: ProjectEndDate | None = None
    jira_url: ProjectJiraUrl | None = None
    status: ProjectStatus | None = None

    @staticmethod
    def generate(project: Project) -> "ProjectPage":
        properties: list[ProjectName | ProjectStartDate | ProjectEndDate | ProjectJiraUrl | ProjectStatus] = [
            ProjectName.from_plain_text(project.name),
            ProjectStartDate.from_start_date(project.start_date),
        ]
        if project.end_date:
            properties.append(ProjectEndDate.from_start_date(project.end_date))
        if project.jira_url:
            properties.append(ProjectJiraUrl.from_url(project.jira_url))
        if project.status:
            properties.append(ProjectStatus.from_status_name(project.status.value))
        return ProjectPage.create(properties=properties)  # type: ignore[no-any-return]

    def to_domain(self) -> Project:
        start_date_prop = self.get_date("開始日")
        end_date_prop = self.get_date("完了日")
        jira_url_prop = self.get_url("Jira")
        status_prop = self.get_status("ステータス")

        # start_dateは必須なのでNoneチェック
        if start_date_prop.start_date is None:
            msg = "start_date is required"
            raise ValueError(msg)

        status = ToDoStatusEnum(status_prop.status_name) if status_prop.status_name else None

        return Project(
            name=self.get_title_text(),
            start_date=start_date_prop.start_date,
            end_date=end_date_prop.start_date if end_date_prop.start_date else None,
            jira_url=jira_url_prop.url if jira_url_prop else None,
            status=status,
        )

    def to_inserted(self) -> InsertedProject:
        start_date_prop = self.get_date("開始日")
        end_date_prop = self.get_date("完了日")
        jira_url_prop = self.get_url("Jira")
        status_prop = self.get_status("ステータス")

        if start_date_prop.start_date is None:
            msg = "start_date is required"
            raise ValueError(msg)

        status = ToDoStatusEnum(status_prop.status_name) if status_prop.status_name else None

        return InsertedProject(
            id=self.id,
            name=self.get_title_text(),
            start_date=start_date_prop.start_date,
            end_date=end_date_prop.start_date if end_date_prop.start_date else None,
            jira_url=jira_url_prop.url if jira_url_prop else None,
            status=status,
        )


class NotionProjectRepository:
    def __init__(self) -> None:
        self.client = Lotion.get_instance()

    def save(self, project: Project) -> InsertedProject:
        notion_project = ProjectPage.generate(project)
        page = self.client.create_page(notion_project)
        return InsertedProject(
            id=page.id,
            name=project.name,
            start_date=project.start_date,
            end_date=project.end_date,
            jira_url=project.jira_url,
            status=project.status,
        )

    def find(self, page_id: str) -> Project:
        notion_page = self.client.retrieve_page(page_id, cls=ProjectPage)
        return notion_page.to_domain()  # type: ignore[no-any-return]

    def find_by_jira_url(self, jira_url: str) -> InsertedProject | None:
        """Jira URLでプロジェクトを検索する"""
        filter_param = Builder.create().add(ProjectJiraUrl.from_url(jira_url), Cond.EQUALS).build()
        pages: list[ProjectPage] = self.client.retrieve_database(
            database_id=project_db.DATABASE_ID, filter_param=filter_param, cls=ProjectPage
        )
        if not pages:
            return None
        return pages[0].to_inserted()

    def fetch_all_jira_urls(self) -> set[str]:
        """すべてのプロジェクトからJira URLの一覧を取得する"""
        filter_param = Builder.create().add(ProjectJiraUrl, Cond.IS_NOT_EMPTY).build()
        pages: list[ProjectPage] = self.client.retrieve_database(
            database_id=project_db.DATABASE_ID, filter_param=filter_param, cls=ProjectPage
        )
        jira_urls: set[str] = set()
        for page in pages:
            jira_url_prop = page.get_url("Jira")
            if jira_url_prop and jira_url_prop.url:
                jira_urls.add(jira_url_prop.url)
        return jira_urls

    def fetch_projects_with_jira_url(self) -> list[InsertedProject]:
        """Jira URLを持つすべてのプロジェクトを取得する"""
        filter_param = Builder.create().add(ProjectJiraUrl, Cond.IS_NOT_EMPTY).build()
        pages: list[ProjectPage] = self.client.retrieve_database(
            database_id=project_db.DATABASE_ID, filter_param=filter_param, cls=ProjectPage
        )
        return [page.to_inserted() for page in pages]

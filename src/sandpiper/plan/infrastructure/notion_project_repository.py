from lotion import BasePage, Lotion, notion_database  # type: ignore[import-untyped]

from sandpiper.plan.domain.project import InsertedProject, Project
from sandpiper.shared.notion.database_config import DatabaseId
from sandpiper.shared.notion.notion_props import ProjectEndDate, ProjectName, ProjectStartDate


@notion_database(DatabaseId.PROJECT)
class ProjectPage(BasePage):  # type: ignore[misc]
    name: ProjectName
    start_date: ProjectStartDate
    end_date: ProjectEndDate | None = None

    @staticmethod
    def generate(project: Project) -> "ProjectPage":
        properties = [
            ProjectName.from_plain_text(project.name),
            ProjectStartDate.from_start_date(project.start_date),
        ]
        if project.end_date:
            properties.append(ProjectEndDate.from_start_date(project.end_date))
        return ProjectPage.create(properties=properties)  # type: ignore[no-any-return]

    def to_domain(self) -> Project:
        start_date_prop = self.get_date("開始日")
        end_date_prop = self.get_date("終了日")

        # start_dateは必須なのでNoneチェック
        if start_date_prop.start_date is None:
            msg = "start_date is required"
            raise ValueError(msg)

        return Project(
            name=self.get_title_text(),
            start_date=start_date_prop.start_date,
            end_date=end_date_prop.start_date if end_date_prop.start_date else None,
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
        )

    def find(self, page_id: str) -> Project:
        notion_page = self.client.retrieve_page(page_id, cls=ProjectPage)
        return notion_page.to_domain()  # type: ignore[no-any-return]

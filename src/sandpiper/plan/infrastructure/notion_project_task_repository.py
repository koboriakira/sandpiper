from lotion import BasePage, Lotion, notion_database  # type: ignore[import-untyped]

from sandpiper.plan.domain.project_task import InsertedProjectTask, ProjectTask
from sandpiper.shared.notion.database_config import DatabaseId
from sandpiper.shared.notion.notion_props import ProjectTaskName, ProjectTaskProjectProp, ProjectTaskStatus
from sandpiper.shared.valueobject.todo_status_enum import ToDoStatusEnum


@notion_database(DatabaseId.PROJECT_TASK)
class ProjectTaskPage(BasePage):  # type: ignore[misc]
    name: ProjectTaskName
    status: ProjectTaskStatus
    project_relation: ProjectTaskProjectProp

    @staticmethod
    def generate(project_task: ProjectTask) -> "ProjectTaskPage":
        properties = [
            ProjectTaskName.from_plain_text(project_task.title),
            ProjectTaskStatus.from_status_name(project_task.status.value),
            ProjectTaskProjectProp.from_id(project_task.project_id),
        ]
        return ProjectTaskPage.create(properties=properties)  # type: ignore[no-any-return]

    def to_domain(self) -> ProjectTask:
        status = self.get_status("ステータス")
        project = self.get_relation("プロジェクト").id_list
        return ProjectTask(
            title=self.get_title_text(),
            status=ToDoStatusEnum(status.status_name),
            project_id=project[0] if project else "",
        )


class NotionProjectTaskRepository:
    def __init__(self) -> None:
        self.client = Lotion.get_instance()

    def save(self, project_task: ProjectTask) -> InsertedProjectTask:
        notion_project_task = ProjectTaskPage.generate(project_task)
        page = self.client.create_page(notion_project_task)
        return InsertedProjectTask(
            id=page.id,
            title=project_task.title,
            status=project_task.status,
            project_id=project_task.project_id,
        )

    def start(self, page_id: str) -> bool:
        """プロジェクトタスクのステータスをInProgressに更新する

        Args:
            page_id: プロジェクトタスクのページID

        Returns:
            bool: 更新が実行された場合True、すでにInProgressの場合False
        """
        page = self.client.retrieve_page(page_id, ProjectTaskPage)
        current_status = page.get_status("ステータス").status_name
        if current_status == ToDoStatusEnum.IN_PROGRESS.value:
            return False
        page.set_prop(ProjectTaskStatus.from_status_name(ToDoStatusEnum.IN_PROGRESS.value))
        self.client.update(page)
        return True

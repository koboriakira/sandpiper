from lotion import notion_prop
from lotion.properties import Date, Status, Title, Url

DATABASE_ID = "458c69ce4e1c49fe810cf26c2291e294"


@notion_prop("名前")
class ProjectName(Title): ...


@notion_prop("開始日")
class ProjectStartDate(Date): ...


@notion_prop("完了日")
class ProjectEndDate(Date): ...


@notion_prop("Jira")
class ProjectJiraUrl(Url): ...


@notion_prop("Claude")
class ProjectClaudeUrl(Url): ...


@notion_prop("ステータス")
class ProjectStatus(Status): ...

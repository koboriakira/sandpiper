from lotion import notion_prop  # type: ignore[import-untyped]
from lotion.properties import Date, Title, Url  # type: ignore[import-untyped]

DATABASE_ID = "458c69ce4e1c49fe810cf26c2291e294"


@notion_prop("名前")
class ProjectName(Title):  # type: ignore[misc]
    ...


@notion_prop("開始日")
class ProjectStartDate(Date):  # type: ignore[misc]
    ...


@notion_prop("終了日")
class ProjectEndDate(Date):  # type: ignore[misc]
    ...


@notion_prop("Jira")
class ProjectJiraUrl(Url):  # type: ignore[misc]
    ...

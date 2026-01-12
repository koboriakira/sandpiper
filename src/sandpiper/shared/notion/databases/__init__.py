"""Notion database configurations and properties.

Each database has its own module with DATABASE_ID and related property classes.
"""

from sandpiper.shared.notion.databases import (
    calendar,
    clips,
    inbox,
    project,
    project_task,
    recipe,
    routine,
    shopping,
    someday,
    todo,
)
from sandpiper.shared.notion.databases.calendar import (
    CalendarEventCategory,
    CalendarEventEndDate,
    CalendarEventName,
    CalendarEventStartDate,
)
from sandpiper.shared.notion.databases.clips import (
    ClipsAutoFetchTitle,
    ClipsName,
    ClipsTypeProp,
    ClipsUrl,
)
from sandpiper.shared.notion.databases.inbox import (
    InboxName,
    InboxType,
    InboxTypeProp,
    InboxUrl,
)
from sandpiper.shared.notion.databases.project import (
    ProjectEndDate,
    ProjectJiraUrl,
    ProjectName,
    ProjectStartDate,
)
from sandpiper.shared.notion.databases.project_task import (
    ProjectTaskContext,
    ProjectTaskName,
    ProjectTaskProjectProp,
    ProjectTaskStatus,
)
from sandpiper.shared.notion.databases.recipe import (
    RecipeIngredientsProp,
    RecipeName,
    RecipeReferenceProp,
)
from sandpiper.shared.notion.databases.routine import (
    RoutineContext,
    RoutineExecutionTime,
    RoutineNextDate,
)
from sandpiper.shared.notion.databases.shopping import ShoppingName
from sandpiper.shared.notion.databases.someday import (
    SomedayDoTomorrow,
    SomedayIsDeleted,
    SomedayName,
    SomedayTiming,
)
from sandpiper.shared.notion.databases.todo import (
    TodoContext,
    TodoExecutionTime,
    TodoIsTodayProp,
    TodoKindProp,
    TodoLogDate,
    TodoName,
    TodoProjectProp,
    TodoProjectTaskProp,
    TodoSection,
    TodoStatus,
)


class DatabaseId:
    """Database IDs for backward compatibility."""

    ROUTINE = routine.DATABASE_ID
    TODO = todo.DATABASE_ID
    PROJECT_TASK = project_task.DATABASE_ID
    PROJECT = project.DATABASE_ID
    CALENDAR = calendar.DATABASE_ID
    RECIPE = recipe.DATABASE_ID
    SHOPPING = shopping.DATABASE_ID
    SOMEDAY_LIST = someday.DATABASE_ID
    INBOX = inbox.DATABASE_ID
    CLIPS = clips.DATABASE_ID


__all__ = [
    "CalendarEventCategory",
    "CalendarEventEndDate",
    "CalendarEventName",
    "CalendarEventStartDate",
    "ClipsAutoFetchTitle",
    "ClipsName",
    "ClipsTypeProp",
    "ClipsUrl",
    "DatabaseId",
    "InboxName",
    "InboxType",
    "InboxTypeProp",
    "InboxUrl",
    "ProjectEndDate",
    "ProjectJiraUrl",
    "ProjectName",
    "ProjectStartDate",
    "ProjectTaskContext",
    "ProjectTaskName",
    "ProjectTaskProjectProp",
    "ProjectTaskStatus",
    "RecipeIngredientsProp",
    "RecipeName",
    "RecipeReferenceProp",
    "RoutineContext",
    "RoutineExecutionTime",
    "RoutineNextDate",
    "ShoppingName",
    "SomedayDoTomorrow",
    "SomedayIsDeleted",
    "SomedayName",
    "SomedayTiming",
    "TodoContext",
    "TodoExecutionTime",
    "TodoIsTodayProp",
    "TodoKindProp",
    "TodoLogDate",
    "TodoName",
    "TodoProjectProp",
    "TodoProjectTaskProp",
    "TodoSection",
    "TodoStatus",
    "calendar",
    "clips",
    "inbox",
    "project",
    "project_task",
    "recipe",
    "routine",
    "shopping",
    "someday",
    "todo",
]

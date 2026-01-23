from enum import Enum


class ToDoStatusEnum(Enum):
    TODO = "ToDo"
    ICEBOX = "Icebox"
    IN_PROGRESS = "InProgress"
    SUSPEND = "Suspend"
    DONE = "Done"
    TRASH = "Trash"

from enum import Enum


class ToDoKind(Enum):
    SCHEDULE = "スケジュール"
    PROJECT = "プロジェクト"
    REPEAT = "リピート"
    INTERRUPTION = "差し込み"
    SINGLE = "単発"
    SUBTASK = "サブタスク"

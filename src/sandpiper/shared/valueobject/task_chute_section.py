from datetime import datetime
from enum import Enum

from sandpiper.shared.utils.date_utils import jst_now


class TaskChuteSection(Enum):
    A_07_10 = "A_07_10"
    B_10_13 = "B_10_13"
    C_13_17 = "C_13_17"
    D_17_19 = "D_17_19"
    E_19_22 = "E_19_22"
    F_22_24 = "F_22_24"
    G_24_07 = "G_24_07"

    @staticmethod
    def new(dt: datetime | None = None) -> "TaskChuteSection":
        """新しいセクションを返す"""
        current_hour = (dt if dt is not None else jst_now()).hour
        if 7 <= current_hour < 10:
            return TaskChuteSection.A_07_10
        if 10 <= current_hour < 13:
            return TaskChuteSection.B_10_13
        if 13 <= current_hour < 17:
            return TaskChuteSection.C_13_17
        if 17 <= current_hour < 19:
            return TaskChuteSection.D_17_19
        if 19 <= current_hour < 22:
            return TaskChuteSection.E_19_22
        if 22 <= current_hour < 24:
            return TaskChuteSection.F_22_24
        return TaskChuteSection.G_24_07

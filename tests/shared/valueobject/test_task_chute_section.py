from datetime import datetime

import pytest

from sandpiper.shared.utils.date_utils import JST
from sandpiper.shared.valueobject.task_chute_section import TaskChuteSection


class TestTaskChuteSection:
    @pytest.mark.parametrize("hour, expected_section", [
        (7, TaskChuteSection.A_07_10),
        (8, TaskChuteSection.A_07_10),
        (9, TaskChuteSection.A_07_10),
        (10, TaskChuteSection.B_10_13),
        (11, TaskChuteSection.B_10_13),
        (12, TaskChuteSection.B_10_13),
        (13, TaskChuteSection.C_13_17),
        (14, TaskChuteSection.C_13_17),
        (16, TaskChuteSection.C_13_17),
        (17, TaskChuteSection.D_17_19),
        (18, TaskChuteSection.D_17_19),
        (19, TaskChuteSection.E_19_22),
        (20, TaskChuteSection.E_19_22),
        (21, TaskChuteSection.E_19_22),
        (22, TaskChuteSection.F_22_24),
        (23, TaskChuteSection.F_22_24),
        (0, TaskChuteSection.G_24_07),  # 0時
        (1, TaskChuteSection.G_24_07),
        (2, TaskChuteSection.G_24_07),
        (3, TaskChuteSection.G_24_07),
        (4, TaskChuteSection.G_24_07),
        (5, TaskChuteSection.G_24_07),
        (6, TaskChuteSection.G_24_07),
    ])
    def test_new_with_specific_hour(self, hour: int, expected_section: TaskChuteSection):
        # 時刻を境界値で明確にテスト
        dt = datetime(2024, 1, 15, hour, 0, 0, tzinfo=JST)
        result = TaskChuteSection.new(dt)
        assert result == expected_section

    def test_new_without_datetime(self):
        # datetime引数なしでも実行可能であることを確認
        result = TaskChuteSection.new()
        assert isinstance(result, TaskChuteSection)

    def test_new_with_none_datetime(self):
        # None指定時も現在時刻で実行されることを確認
        result = TaskChuteSection.new(None)
        assert isinstance(result, TaskChuteSection)

    def test_enum_values(self):
        # Enumの各値が正しく定義されていることを確認
        assert TaskChuteSection.A_07_10.value == "A_07_10"
        assert TaskChuteSection.B_10_13.value == "B_10_13"
        assert TaskChuteSection.C_13_17.value == "C_13_17"
        assert TaskChuteSection.D_17_19.value == "D_17_19"
        assert TaskChuteSection.E_19_22.value == "E_19_22"
        assert TaskChuteSection.F_22_24.value == "F_22_24"
        assert TaskChuteSection.G_24_07.value == "G_24_07"

    def test_all_enum_members_exist(self):
        # すべてのセクションが列挙されていることを確認
        expected_members = {
            "A_07_10", "B_10_13", "C_13_17", "D_17_19",
            "E_19_22", "F_22_24", "G_24_07"
        }
        actual_members = {member.value for member in TaskChuteSection}
        assert actual_members == expected_members

    # 境界値の詳細テスト
    def test_boundary_at_7am(self):
        dt_6_59 = datetime(2024, 1, 15, 6, 59, 59, tzinfo=JST)
        dt_7_00 = datetime(2024, 1, 15, 7, 0, 0, tzinfo=JST)

        assert TaskChuteSection.new(dt_6_59) == TaskChuteSection.G_24_07
        assert TaskChuteSection.new(dt_7_00) == TaskChuteSection.A_07_10

    def test_boundary_at_10am(self):
        dt_9_59 = datetime(2024, 1, 15, 9, 59, 59, tzinfo=JST)
        dt_10_00 = datetime(2024, 1, 15, 10, 0, 0, tzinfo=JST)

        assert TaskChuteSection.new(dt_9_59) == TaskChuteSection.A_07_10
        assert TaskChuteSection.new(dt_10_00) == TaskChuteSection.B_10_13

    def test_boundary_at_midnight(self):
        dt_23_59 = datetime(2024, 1, 15, 23, 59, 59, tzinfo=JST)
        dt_00_00 = datetime(2024, 1, 16, 0, 0, 0, tzinfo=JST)  # 翌日の0時

        assert TaskChuteSection.new(dt_23_59) == TaskChuteSection.F_22_24
        assert TaskChuteSection.new(dt_00_00) == TaskChuteSection.G_24_07

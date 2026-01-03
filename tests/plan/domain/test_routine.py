from datetime import date

from sandpiper.plan.domain.routine import Routine
from sandpiper.plan.domain.routine_cycle import RoutineCycle
from sandpiper.shared.valueobject.task_chute_section import TaskChuteSection


class TestRoutine:
    def setup_method(self):
        self.test_cycle = RoutineCycle.DAILY
        self.test_routine = Routine(
            id="test-routine-1",
            title="テストルーティン",
            date=date(2024, 1, 15),
            section=TaskChuteSection.A_07_10,
            cycle=self.test_cycle,
        )

    def test_routine_creation(self):
        """Routineの基本的な作成をテスト"""
        # Assert
        assert self.test_routine.id == "test-routine-1"
        assert self.test_routine.title == "テストルーティン"
        assert self.test_routine.date == date(2024, 1, 15)
        assert self.test_routine.section == TaskChuteSection.A_07_10
        assert self.test_routine.cycle == self.test_cycle

    def test_routine_dataclass_fields(self):
        """Routineがdataclassとして正しく定義されていることをテスト"""
        # Arrange
        routine = Routine(
            id="test-id",
            title="Test Title",
            date=date(2024, 2, 1),
            section=TaskChuteSection.B_10_13,
            cycle=RoutineCycle.WEEKLY_TUE_FRI,
        )

        # Assert
        assert hasattr(routine, "__dataclass_fields__")
        assert "id" in routine.__dataclass_fields__
        assert "title" in routine.__dataclass_fields__
        assert "date" in routine.__dataclass_fields__
        assert "section" in routine.__dataclass_fields__
        assert "cycle" in routine.__dataclass_fields__

    def test_next_cycle_with_default_basis_date(self):
        """デフォルトのbasis_date(self.date)でのnext_cycleをテスト"""
        # Arrange - 毎日のサイクルを使用
        daily_cycle = RoutineCycle.DAILY
        routine = Routine(
            id="daily-routine",
            title="毎日のルーティン",
            date=date(2024, 1, 15),
            section=TaskChuteSection.C_13_17,
            cycle=daily_cycle,
        )

        # Act
        next_routine = routine.next_cycle()

        # Assert
        assert next_routine.id == routine.id
        assert next_routine.title == routine.title
        assert next_routine.section == routine.section
        assert next_routine.cycle == routine.cycle
        # 毎日なので次の日になる
        assert next_routine.date == date(2024, 1, 16)

    def test_next_cycle_with_explicit_basis_date(self):
        """明示的なbasis_dateでのnext_cycleをテスト"""
        # Arrange
        weekly_cycle = RoutineCycle.WEEKLY_TUE_FRI
        routine = Routine(
            id="weekly-routine",
            title="週次ルーティン",
            date=date(2024, 1, 15),  # 月曜日
            section=TaskChuteSection.D_17_19,
            cycle=weekly_cycle,
        )

        explicit_basis = date(2024, 1, 20)  # 土曜日

        # Act
        next_routine = routine.next_cycle(basis_date=explicit_basis)

        # Assert
        assert next_routine.id == routine.id
        assert next_routine.title == routine.title
        assert next_routine.section == routine.section
        assert next_routine.cycle == routine.cycle
        # basis_dateから次の火曜日を計算
        # 2024/1/20(土) → 次の火曜日は2024/1/23
        assert next_routine.date == date(2024, 1, 23)

    def test_next_cycle_preserves_original_routine(self):
        """next_cycleが元のroutineを変更しないことをテスト"""
        # Arrange
        original_date = date(2024, 1, 10)
        routine = Routine(
            id="preserve-test",
            title="保持テスト",
            date=original_date,
            section=TaskChuteSection.E_19_22,
            cycle=RoutineCycle.DAILY,
        )

        # Act
        next_routine = routine.next_cycle()

        # Assert - 元のroutineは変更されない
        assert routine.date == original_date
        assert next_routine.date != original_date
        assert routine is not next_routine

    def test_next_cycle_with_none_basis_date(self):
        """basis_date=Noneの場合のnext_cycleをテスト"""
        # Arrange
        routine = Routine(
            id="none-basis-test",
            title="Noneベーステスト",
            date=date(2024, 1, 12),
            section=TaskChuteSection.F_22_24,
            cycle=RoutineCycle.DAILY,
        )

        # Act
        next_routine = routine.next_cycle(basis_date=None)

        # Assert - None指定時はself.dateが使用される
        assert next_routine.date == date(2024, 1, 13)  # 翌日

    def test_next_cycle_with_different_cycles(self):
        """異なるサイクルタイプでのnext_cycleをテスト"""
        base_date = date(2024, 1, 15)  # 月曜日

        # 週次サイクル(火・木)
        weekly_routine = Routine(
            id="weekly-test",
            title="週次テスト",
            date=base_date,
            section=TaskChuteSection.A_07_10,
            cycle=RoutineCycle.WEEKLY_TUE_FRI,
        )

        # Act
        next_weekly = weekly_routine.next_cycle()

        # Assert
        # 月曜日から次の火曜日へ
        assert next_weekly.date == date(2024, 1, 16)

    def test_next_cycle_complex_scenario(self):
        """複雑なシナリオでのnext_cycleをテスト"""
        # Arrange - 週次(水曜日)
        weekly_cycle = RoutineCycle.WEEKLY_WED
        routine = Routine(
            id="weekly-complex",
            title="週次複雑ルーティン",
            date=date(2024, 1, 15),  # 月曜日
            section=TaskChuteSection.G_24_07,
            cycle=weekly_cycle,
        )

        # Act
        next_routine = routine.next_cycle()

        # Assert
        assert next_routine.id == routine.id
        assert next_routine.title == routine.title
        assert next_routine.section == routine.section
        assert next_routine.cycle == routine.cycle
        # 月曜日から次の水曜日になる
        assert next_routine.date == date(2024, 1, 17)

    def test_routine_equality(self):
        """同じ内容のRoutineが等しいことをテスト"""
        # Arrange
        routine1 = Routine(
            id="equal-test",
            title="等価テスト",
            date=date(2024, 1, 20),
            section=TaskChuteSection.B_10_13,
            cycle=RoutineCycle.DAILY,
        )

        routine2 = Routine(
            id="equal-test",
            title="等価テスト",
            date=date(2024, 1, 20),
            section=TaskChuteSection.B_10_13,
            cycle=RoutineCycle.DAILY,
        )

        # Assert - dataclassの自動equality
        assert routine1 == routine2

    def test_routine_immutability_through_next_cycle(self):
        """next_cycleを通じたRoutineの不変性をテスト"""
        # Arrange
        original_routine = Routine(
            id="immutable-test",
            title="不変性テスト",
            date=date(2024, 1, 5),
            section=TaskChuteSection.C_13_17,
            cycle=RoutineCycle.DAILY,
        )

        # Act
        next_routine = original_routine.next_cycle()

        # Assert - 新しいインスタンスが作成される
        assert original_routine is not next_routine
        assert id(original_routine) != id(next_routine)

        # 変更されるのはdateのみ
        assert original_routine.id == next_routine.id
        assert original_routine.title == next_routine.title
        assert original_routine.section == next_routine.section
        assert original_routine.cycle == next_routine.cycle
        assert original_routine.date != next_routine.date

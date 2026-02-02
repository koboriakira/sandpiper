from datetime import date

import pytest

from sandpiper.plan.domain.routine_cycle import RoutineCycle


class TestRoutineCycleNextDate:
    """RoutineCycleのnext_dateメソッドのテストクラス."""

    def test_daily(self):
        """DAILYの場合、翌日が返される."""
        basis_date = date(2026, 1, 15)
        result = RoutineCycle.DAILY.next_date(basis_date)
        assert result == date(2026, 1, 16)

    def test_weekly_tue_fri_on_monday(self):
        """WEEKLY_TUE_FRIの月曜日の場合、次の火曜日が返される."""
        basis_date = date(2026, 1, 5)  # 月曜日
        result = RoutineCycle.WEEKLY_TUE_FRI.next_date(basis_date)
        assert result == date(2026, 1, 6)  # 火曜日

    def test_weekly_tue_fri_on_tuesday(self):
        """WEEKLY_TUE_FRIの火曜日の場合、次の金曜日が返される."""
        basis_date = date(2026, 1, 6)  # 火曜日
        result = RoutineCycle.WEEKLY_TUE_FRI.next_date(basis_date)
        assert result == date(2026, 1, 9)  # 金曜日

    def test_weekly_tue_fri_on_wednesday(self):
        """WEEKLY_TUE_FRIの水曜日の場合、次の金曜日が返される."""
        basis_date = date(2026, 1, 7)  # 水曜日
        result = RoutineCycle.WEEKLY_TUE_FRI.next_date(basis_date)
        assert result == date(2026, 1, 9)  # 金曜日

    def test_weekly_tue_fri_on_friday(self):
        """WEEKLY_TUE_FRIの金曜日の場合、次の火曜日が返される."""
        basis_date = date(2026, 1, 9)  # 金曜日
        result = RoutineCycle.WEEKLY_TUE_FRI.next_date(basis_date)
        assert result == date(2026, 1, 13)  # 火曜日

    def test_weekly_tue_fri_on_saturday(self):
        """WEEKLY_TUE_FRIの土曜日の場合、次の火曜日が返される."""
        basis_date = date(2026, 1, 10)  # 土曜日
        result = RoutineCycle.WEEKLY_TUE_FRI.next_date(basis_date)
        assert result == date(2026, 1, 13)  # 火曜日

    def test_weekly_wed_on_monday(self):
        """WEEKLY_WEDの月曜日の場合、次の水曜日が返される."""
        basis_date = date(2026, 1, 5)  # 月曜日
        result = RoutineCycle.WEEKLY_WED.next_date(basis_date)
        assert result == date(2026, 1, 7)  # 水曜日

    def test_weekly_wed_on_wednesday(self):
        """WEEKLY_WEDの水曜日の場合、次の水曜日が返される."""
        basis_date = date(2026, 1, 7)  # 水曜日
        result = RoutineCycle.WEEKLY_WED.next_date(basis_date)
        assert result == date(2026, 1, 14)  # 水曜日

    def test_weekly_wed_on_thursday(self):
        """WEEKLY_WEDの木曜日の場合、次の水曜日が返される."""
        basis_date = date(2026, 1, 8)  # 木曜日
        result = RoutineCycle.WEEKLY_WED.next_date(basis_date)
        assert result == date(2026, 1, 14)  # 水曜日

    def test_weekly_sat(self):
        """WEEKLY_SATの場合、次の土曜日が返される."""
        basis_date = date(2026, 1, 5)  # 月曜日
        result = RoutineCycle.WEEKLY_SAT.next_date(basis_date)
        assert result == date(2026, 1, 10)  # 土曜日

    def test_weekly_sat_on_saturday(self):
        """WEEKLY_SATの土曜日の場合、次の土曜日が返される."""
        basis_date = date(2026, 1, 10)  # 土曜日
        result = RoutineCycle.WEEKLY_SAT.next_date(basis_date)
        assert result == date(2026, 1, 17)  # 土曜日

    def test_weekly_sun_on_monday(self):
        """WEEKLY_SUNの月曜日の場合、次の日曜日が返される."""
        basis_date = date(2026, 1, 5)  # 月曜日
        result = RoutineCycle.WEEKLY_SUN.next_date(basis_date)
        assert result == date(2026, 1, 11)  # 日曜日

    def test_weekly_sun_on_sunday(self):
        """WEEKLY_SUNの日曜日の場合、次の日曜日が返される."""
        basis_date = date(2026, 1, 11)  # 日曜日
        result = RoutineCycle.WEEKLY_SUN.next_date(basis_date)
        assert result == date(2026, 1, 18)  # 日曜日

    def test_weekly_mon_on_tuesday(self):
        """WEEKLY_MONの火曜日の場合、次の月曜日が返される."""
        basis_date = date(2026, 1, 6)  # 火曜日
        result = RoutineCycle.WEEKLY_MON.next_date(basis_date)
        assert result == date(2026, 1, 12)  # 月曜日

    def test_weekly_mon_on_monday(self):
        """WEEKLY_MONの月曜日の場合、次の月曜日が返される."""
        basis_date = date(2026, 1, 5)  # 月曜日
        result = RoutineCycle.WEEKLY_MON.next_date(basis_date)
        assert result == date(2026, 1, 12)  # 月曜日

    def test_weekly_tue_on_wednesday(self):
        """WEEKLY_TUEの水曜日の場合、次の火曜日が返される."""
        basis_date = date(2026, 1, 7)  # 水曜日
        result = RoutineCycle.WEEKLY_TUE.next_date(basis_date)
        assert result == date(2026, 1, 13)  # 火曜日

    def test_weekly_tue_on_tuesday(self):
        """WEEKLY_TUEの火曜日の場合、次の火曜日が返される."""
        basis_date = date(2026, 1, 6)  # 火曜日
        result = RoutineCycle.WEEKLY_TUE.next_date(basis_date)
        assert result == date(2026, 1, 13)  # 火曜日

    def test_weekly_thu_on_friday(self):
        """WEEKLY_THUの金曜日の場合、次の木曜日が返される."""
        basis_date = date(2026, 1, 9)  # 金曜日
        result = RoutineCycle.WEEKLY_THU.next_date(basis_date)
        assert result == date(2026, 1, 15)  # 木曜日

    def test_weekly_thu_on_thursday(self):
        """WEEKLY_THUの木曜日の場合、次の木曜日が返される."""
        basis_date = date(2026, 1, 8)  # 木曜日
        result = RoutineCycle.WEEKLY_THU.next_date(basis_date)
        assert result == date(2026, 1, 15)  # 木曜日

    def test_weekly_fri_on_saturday(self):
        """WEEKLY_FRIの土曜日の場合、次の金曜日が返される."""
        basis_date = date(2026, 1, 10)  # 土曜日
        result = RoutineCycle.WEEKLY_FRI.next_date(basis_date)
        assert result == date(2026, 1, 16)  # 金曜日

    def test_weekly_fri_on_friday(self):
        """WEEKLY_FRIの金曜日の場合、次の金曜日が返される."""
        basis_date = date(2026, 1, 9)  # 金曜日
        result = RoutineCycle.WEEKLY_FRI.next_date(basis_date)
        assert result == date(2026, 1, 16)  # 金曜日

    def test_after_3_days(self):
        """AFTER_3_DAYSの場合、3日後が返される."""
        basis_date = date(2026, 1, 15)
        result = RoutineCycle.AFTER_3_DAYS.next_date(basis_date)
        assert result == date(2026, 1, 18)

    def test_after_7_days(self):
        """AFTER_7_DAYSの場合、7日後が返される."""
        basis_date = date(2026, 1, 15)
        result = RoutineCycle.AFTER_7_DAYS.next_date(basis_date)
        assert result == date(2026, 1, 22)

    def test_next_week(self):
        """NEXT_WEEKの場合、7日後が返される."""
        basis_date = date(2026, 1, 15)
        result = RoutineCycle.NEXT_WEEK.next_date(basis_date)
        assert result == date(2026, 1, 22)

    def test_after_20_days(self):
        """AFTER_20_DAYSの場合、20日後が返される."""
        basis_date = date(2026, 1, 15)
        result = RoutineCycle.AFTER_20_DAYS.next_date(basis_date)
        assert result == date(2026, 2, 4)

    def test_monthly_1st(self):
        """MONTHLY_1STの場合、翌月1日が返される."""
        basis_date = date(2026, 1, 15)
        result = RoutineCycle.MONTHLY_1ST.next_date(basis_date)
        assert result == date(2026, 2, 1)

    def test_monthly_1st_december(self):
        """MONTHLY_1STで12月の場合、翌年1月1日が返される."""
        basis_date = date(2025, 12, 15)
        result = RoutineCycle.MONTHLY_1ST.next_date(basis_date)
        assert result == date(2026, 1, 1)

    def test_monthly_2nd_before_2nd(self):
        """MONTHLY_2NDで2日より前の場合、当月2日が返される."""
        basis_date = date(2026, 1, 1)
        result = RoutineCycle.MONTHLY_2ND.next_date(basis_date)
        assert result == date(2026, 1, 2)

    def test_monthly_2nd_after_2nd(self):
        """MONTHLY_2NDで2日以降の場合、翌月2日が返される."""
        basis_date = date(2026, 1, 3)
        result = RoutineCycle.MONTHLY_2ND.next_date(basis_date)
        assert result == date(2026, 2, 2)

    def test_monthly_2nd_on_2nd(self):
        """MONTHLY_2NDで2日の場合、翌月2日が返される."""
        basis_date = date(2026, 1, 2)
        result = RoutineCycle.MONTHLY_2ND.next_date(basis_date)
        assert result == date(2026, 2, 2)

    def test_monthly_2nd_december(self):
        """MONTHLY_2NDで12月の場合、翌年1月2日が返される."""
        basis_date = date(2025, 12, 15)
        result = RoutineCycle.MONTHLY_2ND.next_date(basis_date)
        assert result == date(2026, 1, 2)

    def test_monthly_25th_before_25th(self):
        """MONTHLY_25THで25日より前の場合、当月25日が返される."""
        basis_date = date(2026, 1, 15)
        result = RoutineCycle.MONTHLY_25TH.next_date(basis_date)
        assert result == date(2026, 1, 25)

    def test_monthly_25th_after_25th(self):
        """MONTHLY_25THで25日以降の場合、翌月25日が返される."""
        basis_date = date(2026, 1, 26)
        result = RoutineCycle.MONTHLY_25TH.next_date(basis_date)
        assert result == date(2026, 2, 25)

    def test_monthly_25th_on_25th(self):
        """MONTHLY_25THで25日の場合、翌月25日が返される."""
        basis_date = date(2026, 1, 25)
        result = RoutineCycle.MONTHLY_25TH.next_date(basis_date)
        assert result == date(2026, 2, 25)

    def test_month_end_january(self):
        """MONTH_ENDの1月の場合、1月31日が返される."""
        basis_date = date(2026, 1, 15)
        result = RoutineCycle.MONTH_END.next_date(basis_date)
        assert result == date(2026, 1, 31)

    def test_month_end_february(self):
        """MONTH_ENDの2月の場合、2月末日が返される."""
        basis_date = date(2026, 2, 15)
        result = RoutineCycle.MONTH_END.next_date(basis_date)
        assert result == date(2026, 2, 28)

    def test_month_end_february_leap_year(self):
        """MONTH_ENDの閏年2月の場合、2月29日が返される."""
        basis_date = date(2024, 2, 15)
        result = RoutineCycle.MONTH_END.next_date(basis_date)
        assert result == date(2024, 2, 29)

    def test_month_end_december(self):
        """MONTH_ENDの12月の場合、12月31日が返される."""
        basis_date = date(2025, 12, 15)
        result = RoutineCycle.MONTH_END.next_date(basis_date)
        assert result == date(2025, 12, 31)

    def test_first_third_fri_before_first(self):
        """FIRST_THIRD_FRIで第1金曜日より前の場合、第1金曜日が返される."""
        basis_date = date(2026, 1, 1)  # 木曜日
        result = RoutineCycle.FIRST_THIRD_FRI.next_date(basis_date)
        assert result == date(2026, 1, 2)  # 第1金曜日

    def test_first_third_fri_between_first_and_third(self):
        """FIRST_THIRD_FRIで第1と第3金曜日の間の場合、第3金曜日が返される."""
        basis_date = date(2026, 1, 10)  # 土曜日(第1金曜日の後)
        result = RoutineCycle.FIRST_THIRD_FRI.next_date(basis_date)
        assert result == date(2026, 1, 16)  # 第3金曜日

    def test_first_third_fri_after_third(self):
        """FIRST_THIRD_FRIで第3金曜日より後の場合、翌月の第1金曜日が返される."""
        basis_date = date(2026, 1, 20)  # 火曜日(第3金曜日の後)
        result = RoutineCycle.FIRST_THIRD_FRI.next_date(basis_date)
        assert result == date(2026, 2, 6)  # 翌月の第1金曜日

    def test_first_third_thu_before_first(self):
        """FIRST_THIRD_THUで第1木曜日の場合、第3木曜日が返される."""
        basis_date = date(2026, 1, 1)  # 木曜日(第1木曜日)
        result = RoutineCycle.FIRST_THIRD_THU.next_date(basis_date)
        assert result == date(2026, 1, 15)  # 第3木曜日

    def test_first_third_thu_between_first_and_third(self):
        """FIRST_THIRD_THUで第1と第3木曜日の間の場合、第3木曜日が返される."""
        basis_date = date(2026, 1, 10)  # 土曜日(第1木曜日の後)
        result = RoutineCycle.FIRST_THIRD_THU.next_date(basis_date)
        assert result == date(2026, 1, 15)  # 第3木曜日

    def test_first_third_thu_after_third(self):
        """FIRST_THIRD_THUで第3木曜日より後の場合、翌月の第1木曜日が返される."""
        basis_date = date(2026, 1, 20)  # 火曜日(第3木曜日の後)
        result = RoutineCycle.FIRST_THIRD_THU.next_date(basis_date)
        assert result == date(2026, 2, 5)  # 翌月の第1木曜日


class TestRoutineCycleFromText:
    """RoutineCycleのfrom_textメソッドのテストクラス."""

    def test_from_text_daily(self):
        """from_textで「毎日」からDAILYが取得できる."""
        result = RoutineCycle.from_text("毎日")
        assert result == RoutineCycle.DAILY

    def test_from_text_weekly_tue_fri(self):
        """from_textで「毎週火・金」からWEEKLY_TUE_FRIが取得できる."""
        result = RoutineCycle.from_text("毎週火・金")
        assert result == RoutineCycle.WEEKLY_TUE_FRI

    def test_from_text_first_third_thu(self):
        """from_textで「第1・3木」からFIRST_THIRD_THUが取得できる."""
        result = RoutineCycle.from_text("第1・3木")
        assert result == RoutineCycle.FIRST_THIRD_THU

    def test_from_text_weekly_sun(self):
        """from_textで「毎週日」からWEEKLY_SUNが取得できる."""
        result = RoutineCycle.from_text("毎週日")
        assert result == RoutineCycle.WEEKLY_SUN

    def test_from_text_weekly_mon(self):
        """from_textで「毎週月」からWEEKLY_MONが取得できる."""
        result = RoutineCycle.from_text("毎週月")
        assert result == RoutineCycle.WEEKLY_MON

    def test_from_text_weekly_tue(self):
        """from_textで「毎週火」からWEEKLY_TUEが取得できる."""
        result = RoutineCycle.from_text("毎週火")
        assert result == RoutineCycle.WEEKLY_TUE

    def test_from_text_weekly_thu(self):
        """from_textで「毎週木」からWEEKLY_THUが取得できる."""
        result = RoutineCycle.from_text("毎週木")
        assert result == RoutineCycle.WEEKLY_THU

    def test_from_text_weekly_fri(self):
        """from_textで「毎週金」からWEEKLY_FRIが取得できる."""
        result = RoutineCycle.from_text("毎週金")
        assert result == RoutineCycle.WEEKLY_FRI

    def test_from_text_monthly_2nd(self):
        """from_textで「毎月2日」からMONTHLY_2NDが取得できる."""
        result = RoutineCycle.from_text("毎月2日")
        assert result == RoutineCycle.MONTHLY_2ND

    def test_from_text_not_found(self):
        """from_textで存在しないテキストの場合、ValueErrorが発生する."""
        with pytest.raises(ValueError, match="RoutineCycle not found: 存在しない"):
            RoutineCycle.from_text("存在しない")

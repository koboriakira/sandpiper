from datetime import date
import pytest

from sandpiper.plan.domain.routine_cycle import (
    add_a_month, 
    get_first_friday, 
    get_third_friday,
    get_first_thursday,
    get_third_thursday
)


class TestAddAMonth:
    def test_add_a_month_normal(self):
        """通常月での翌月取得をテスト"""
        # Arrange
        test_date = date(2024, 3, 15)
        
        # Act
        year, month = add_a_month(test_date)
        
        # Assert
        assert year == 2024
        assert month == 4

    def test_add_a_month_december_to_january(self):
        """12月から1月への翌月取得をテスト"""
        # Arrange
        test_date = date(2024, 12, 25)
        
        # Act
        year, month = add_a_month(test_date)
        
        # Assert
        assert year == 2025
        assert month == 1

    def test_add_a_month_november_to_december(self):
        """11月から12月への翌月取得をテスト"""
        # Arrange
        test_date = date(2024, 11, 10)
        
        # Act
        year, month = add_a_month(test_date)
        
        # Assert
        assert year == 2024
        assert month == 12

    def test_add_a_month_january_to_february(self):
        """1月から2月への翌月取得をテスト"""
        # Arrange
        test_date = date(2024, 1, 1)
        
        # Act
        year, month = add_a_month(test_date)
        
        # Assert
        assert year == 2024
        assert month == 2


class TestGetFirstFriday:
    def test_get_first_friday_march_2024(self):
        """2024年3月の第1金曜日取得をテスト"""
        # Act
        result = get_first_friday(2024, 3)
        
        # Assert
        assert result == date(2024, 3, 1)
        assert result.weekday() == 4  # 金曜日

    def test_get_first_friday_january_2026(self):
        """2026年1月の第1金曜日取得をテスト"""
        # Act
        result = get_first_friday(2026, 1)
        
        # Assert
        assert result == date(2026, 1, 2)
        assert result.weekday() == 4  # 金曜日

    def test_get_first_friday_february_2024(self):
        """2024年2月の第1金曜日取得をテスト"""
        # Act
        result = get_first_friday(2024, 2)
        
        # Assert
        assert result == date(2024, 2, 2)
        assert result.weekday() == 4  # 金曜日

    def test_get_first_friday_december_2024(self):
        """2024年12月の第1金曜日取得をテスト"""
        # Act
        result = get_first_friday(2024, 12)
        
        # Assert
        assert result == date(2024, 12, 6)
        assert result.weekday() == 4  # 金曜日

    def test_get_first_friday_april_2024(self):
        """2024年4月の第1金曜日取得をテスト（4月1日が月曜日のケース）"""
        # Act
        result = get_first_friday(2024, 4)
        
        # Assert
        assert result == date(2024, 4, 5)
        assert result.weekday() == 4  # 金曜日


class TestGetThirdFriday:
    def test_get_third_friday_march_2024(self):
        """2024年3月の第3金曜日取得をテスト"""
        # Act
        result = get_third_friday(2024, 3)
        
        # Assert
        assert result == date(2024, 3, 15)
        assert result.weekday() == 4  # 金曜日

    def test_get_third_friday_january_2026(self):
        """2026年1月の第3金曜日取得をテスト"""
        # Act
        result = get_third_friday(2026, 1)
        
        # Assert
        assert result == date(2026, 1, 16)
        assert result.weekday() == 4  # 金曜日

    def test_get_third_friday_february_2024(self):
        """2024年2月の第3金曜日取得をテスト"""
        # Act
        result = get_third_friday(2024, 2)
        
        # Assert
        assert result == date(2024, 2, 16)
        assert result.weekday() == 4  # 金曜日


class TestGetFirstThursday:
    def test_get_first_thursday_march_2024(self):
        """2024年3月の第1木曜日取得をテスト"""
        # Act
        result = get_first_thursday(2024, 3)
        
        # Assert
        assert result == date(2024, 3, 7)
        assert result.weekday() == 3  # 木曜日

    def test_get_first_thursday_january_2026(self):
        """2026年1月の第1木曜日取得をテスト"""
        # Act
        result = get_first_thursday(2026, 1)
        
        # Assert
        assert result == date(2026, 1, 1)
        assert result.weekday() == 3  # 木曜日

    def test_get_first_thursday_february_2024(self):
        """2024年2月の第1木曜日取得をテスト"""
        # Act
        result = get_first_thursday(2024, 2)
        
        # Assert
        assert result == date(2024, 2, 1)
        assert result.weekday() == 3  # 木曜日

    def test_get_first_thursday_april_2024(self):
        """2024年4月の第1木曜日取得をテスト"""
        # Act
        result = get_first_thursday(2024, 4)
        
        # Assert
        assert result == date(2024, 4, 4)
        assert result.weekday() == 3  # 木曜日


class TestGetThirdThursday:
    def test_get_third_thursday_march_2024(self):
        """2024年3月の第3木曜日取得をテスト"""
        # Act
        result = get_third_thursday(2024, 3)
        
        # Assert
        assert result == date(2024, 3, 21)
        assert result.weekday() == 3  # 木曜日

    def test_get_third_thursday_january_2026(self):
        """2026年1月の第3木曜日取得をテスト"""
        # Act
        result = get_third_thursday(2026, 1)
        
        # Assert
        assert result == date(2026, 1, 15)
        assert result.weekday() == 3  # 木曜日

    def test_get_third_thursday_february_2024(self):
        """2024年2月の第3木曜日取得をテスト"""
        # Act
        result = get_third_thursday(2024, 2)
        
        # Assert
        assert result == date(2024, 2, 15)
        assert result.weekday() == 3  # 木曜日


class TestExceptionCases:
    def test_get_first_friday_no_month_error_impossible(self):
        """通常のカレンダーでは get_first_friday でエラーは発生しない"""
        # すべての月には必ず第1金曜日が存在するため、
        # ValueErrorが発生することは通常ありえない
        # しかし、コードカバレッジのためにエラーケースを想定した場合の動作を確認
        
        # 正常な月では例外は発生しない
        for month in range(1, 13):
            result = get_first_friday(2024, month)
            assert result.weekday() == 4

    def test_get_first_thursday_no_month_error_impossible(self):
        """通常のカレンダーでは get_first_thursday でエラーは発生しない"""
        # すべての月には必ず第1木曜日が存在するため、
        # ValueErrorが発生することは通常ありえない
        
        # 正常な月では例外は発生しない
        for month in range(1, 13):
            result = get_first_thursday(2024, month)
            assert result.weekday() == 3
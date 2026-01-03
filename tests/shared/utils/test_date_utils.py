from datetime import date, datetime, timedelta
from unittest.mock import patch

import pytest

from sandpiper.shared.utils.date_utils import (
    JST,
    DateType,
    _convert_date,
    _convert_datetime,
    convert_to_date_or_datetime,
    jst_now,
    jst_today,
    jst_today_datetime,
    jst_tommorow,
)
from sandpiper.shared.utils.date_utils import __is_datatime as _is_datetime


class TestDateType:
    @pytest.mark.parametrize(
        "value, expected",
        [
            ("2024-01-15", DateType.DATE),
            ("2024-01-15T10:30:00", DateType.DATETIME),
            ("2024-01-15T10:30:00+09:00", DateType.DATETIME),
            ("invalid", DateType.NONE),
            ("", DateType.NONE),
            ("2024-13-01", DateType.NONE),  # 不正な日付
        ],
    )
    def test_get_datetype(self, value: str, expected: DateType):
        result = DateType.get_datetype(value)
        assert result == expected


class TestJSTUtils:
    def test_jst_now(self):
        result = jst_now()
        assert isinstance(result, datetime)
        assert result.tzinfo == JST

    def test_jst_today_datetime(self):
        result = jst_today_datetime()
        assert isinstance(result, datetime)
        assert result.hour == 0
        assert result.minute == 0
        assert result.second == 0
        assert result.microsecond == 0
        assert result.tzinfo == JST

    def test_jst_today_without_previous_day_logic(self):
        result = jst_today()
        assert isinstance(result, date)

    def test_jst_today_with_previous_day_logic_false(self):
        result = jst_today(is_previous_day_until_2am=False)
        assert isinstance(result, date)

    @patch("sandpiper.shared.utils.date_utils.jst_now")
    def test_jst_today_with_previous_day_logic_after_2am(self, mock_jst_now):
        """2時以降でのjst_today()でis_previous_day_until_2am=Trueの場合をテスト（47行目のelse部分）"""
        # Arrange - 2時以降の時刻をモック（例：3時）
        mock_time = datetime(2024, 1, 15, 3, 0, 0)
        mock_jst_now.return_value = mock_time

        # Act
        result = jst_today(is_previous_day_until_2am=True)

        # Assert
        # 2時以降なので前日にはならず、当日のdate()が返される（else部分）
        assert result == date(2024, 1, 15)
        mock_jst_now.assert_called_once()

    def test_jst_tommorow(self):
        today_dt = jst_today_datetime()
        result = jst_tommorow()
        expected = today_dt + timedelta(days=1)
        assert result == expected


class TestConvertToDateOrDatetime:
    def test_convert_none(self):
        result = convert_to_date_or_datetime(None)
        assert result is None

    def test_convert_date_string(self):
        result = convert_to_date_or_datetime("2024-01-15")
        assert isinstance(result, date)
        assert result == date(2024, 1, 15)

    def test_convert_datetime_string(self):
        result = convert_to_date_or_datetime("2024-01-15T10:30:00")
        assert isinstance(result, datetime)
        assert result.year == 2024
        assert result.month == 1
        assert result.day == 15
        assert result.hour == 10
        assert result.minute == 30

    def test_convert_invalid_string(self):
        result = convert_to_date_or_datetime("invalid")
        assert result is None

    def test_convert_date_with_datetime_cls(self):
        result = convert_to_date_or_datetime("2024-01-15", datetime)
        assert isinstance(result, datetime)
        assert result.year == 2024
        assert result.month == 1
        assert result.day == 15
        assert result.hour == 0
        assert result.tzinfo == JST

    def test_convert_datetime_with_date_cls(self):
        result = convert_to_date_or_datetime("2024-01-15T10:30:00", date)
        assert isinstance(result, date)
        assert result == date(2024, 1, 15)


class TestConvertDate:
    def test_convert_date_no_cls(self):
        result = _convert_date("2024-01-15", None)
        assert isinstance(result, date)
        assert result == date(2024, 1, 15)

    def test_convert_date_with_date_cls(self):
        result = _convert_date("2024-01-15", date)
        assert isinstance(result, date)
        assert result == date(2024, 1, 15)

    def test_convert_date_with_datetime_cls(self):
        result = _convert_date("2024-01-15", datetime)
        assert isinstance(result, datetime)
        assert result.year == 2024
        assert result.month == 1
        assert result.day == 15
        assert result.hour == 0
        assert result.tzinfo == JST


class TestConvertDatetime:
    def test_convert_datetime_no_cls(self):
        # 時分秒が設定されている場合
        result = _convert_datetime("2024-01-15T10:30:00", None)
        assert isinstance(result, datetime)
        assert result.hour == 10
        assert result.minute == 30

    def test_convert_datetime_no_cls_midnight(self):
        # 00:00:00の場合はdateオブジェクトを返す
        result = _convert_datetime("2024-01-15T00:00:00", None)
        assert isinstance(result, date)
        assert result == date(2024, 1, 15)

    def test_convert_datetime_with_date_cls(self):
        result = _convert_datetime("2024-01-15T10:30:00", date)
        assert isinstance(result, date)
        assert result == date(2024, 1, 15)

    def test_convert_datetime_with_datetime_cls(self):
        result = _convert_datetime("2024-01-15T10:30:00", datetime)
        assert isinstance(result, datetime)
        assert result.hour == 10
        assert result.minute == 30


class TestIsDatetime:
    def test_is_datetime_with_time(self):
        dt = datetime(2024, 1, 15, 10, 30, 0)
        assert _is_datetime(dt) is True

    def test_is_datetime_midnight(self):
        dt = datetime(2024, 1, 15, 0, 0, 0)
        assert _is_datetime(dt) is False

    def test_is_datetime_with_seconds(self):
        dt = datetime(2024, 1, 15, 0, 0, 30)
        assert _is_datetime(dt) is True

    def test_is_datetime_with_minutes(self):
        dt = datetime(2024, 1, 15, 0, 15, 0)
        assert _is_datetime(dt) is True

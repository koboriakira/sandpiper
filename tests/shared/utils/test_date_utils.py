from datetime import date, datetime, timedelta
from unittest.mock import patch

import pytest

from sandpiper.shared.utils.date_utils import (
    JST,
    DateType,
    _convert_date,
    _convert_datetime,
    _has_time,
    convert_to_date_or_datetime,
    jst_now,
    jst_today,
    jst_today_datetime,
    jst_tommorow,
    jst_tomorrow,
)


class TestDateType:
    """DateType.get_datetype()のテスト."""

    @pytest.mark.parametrize(
        ("value", "expected"),
        [
            ("2024-01-15", DateType.DATE),
            ("2024-01-15T10:30:00", DateType.DATETIME),
            ("2024-01-15T10:30:00+09:00", DateType.DATETIME),
            ("invalid", DateType.NONE),
            ("", DateType.NONE),
            ("2024-13-01", DateType.NONE),  # 不正な日付
        ],
    )
    def test_get_datetype(self, value: str, expected: str) -> None:
        result = DateType.get_datetype(value)
        assert result == expected


class TestJstNow:
    """jst_now()のテスト."""

    def test_returns_datetime_with_jst_timezone(self) -> None:
        result = jst_now()
        assert isinstance(result, datetime)
        assert result.tzinfo == JST


class TestJstTodayDatetime:
    """jst_today_datetime()のテスト."""

    def test_returns_midnight_datetime(self) -> None:
        result = jst_today_datetime()
        assert isinstance(result, datetime)
        assert result.hour == 0
        assert result.minute == 0
        assert result.second == 0
        assert result.microsecond == 0
        assert result.tzinfo == JST


class TestJstToday:
    """jst_today()のテスト."""

    def test_returns_date_without_previous_day_logic(self) -> None:
        result = jst_today()
        assert isinstance(result, date)

    def test_returns_date_with_previous_day_logic_false(self) -> None:
        result = jst_today(is_previous_day_until_2am=False)
        assert isinstance(result, date)

    @patch("sandpiper.shared.utils.date_utils.jst_now")
    def test_returns_previous_day_before_2am(self, mock_jst_now) -> None:
        """午前2時前でis_previous_day_until_2am=Trueの場合は前日を返す."""
        mock_time = datetime(2024, 1, 15, 1, 30, 0, tzinfo=JST)
        mock_jst_now.return_value = mock_time

        result = jst_today(is_previous_day_until_2am=True)

        assert result == date(2024, 1, 14)
        mock_jst_now.assert_called_once()

    @patch("sandpiper.shared.utils.date_utils.jst_now")
    def test_returns_current_day_after_2am(self, mock_jst_now) -> None:
        """午前2時以降でis_previous_day_until_2am=Trueの場合は当日を返す."""
        mock_time = datetime(2024, 1, 15, 3, 0, 0, tzinfo=JST)
        mock_jst_now.return_value = mock_time

        result = jst_today(is_previous_day_until_2am=True)

        assert result == date(2024, 1, 15)
        mock_jst_now.assert_called_once()


class TestJstTomorrow:
    """jst_tomorrow()のテスト."""

    def test_returns_tomorrow_midnight(self) -> None:
        today_dt = jst_today_datetime()
        result = jst_tomorrow()
        expected = today_dt + timedelta(days=1)
        assert result == expected

    def test_backward_compatible_alias(self) -> None:
        """後方互換性エイリアスjst_tommorowが同じ結果を返す."""
        assert jst_tommorow() == jst_tomorrow()


class TestConvertToDateOrDatetime:
    """convert_to_date_or_datetime()のテスト."""

    def test_returns_none_for_none_input(self) -> None:
        result = convert_to_date_or_datetime(None)
        assert result is None

    def test_converts_date_string(self) -> None:
        result = convert_to_date_or_datetime("2024-01-15")
        assert isinstance(result, date)
        assert result == date(2024, 1, 15)

    def test_converts_datetime_string(self) -> None:
        result = convert_to_date_or_datetime("2024-01-15T10:30:00")
        assert isinstance(result, datetime)
        assert result.year == 2024
        assert result.month == 1
        assert result.day == 15
        assert result.hour == 10
        assert result.minute == 30

    def test_returns_none_for_invalid_string(self) -> None:
        result = convert_to_date_or_datetime("invalid")
        assert result is None

    def test_converts_date_to_datetime_with_cls(self) -> None:
        result = convert_to_date_or_datetime("2024-01-15", datetime)
        assert isinstance(result, datetime)
        assert result.year == 2024
        assert result.month == 1
        assert result.day == 15
        assert result.hour == 0
        assert result.tzinfo == JST

    def test_converts_datetime_to_date_with_cls(self) -> None:
        result = convert_to_date_or_datetime("2024-01-15T10:30:00", date)
        assert isinstance(result, date)
        assert result == date(2024, 1, 15)


class TestConvertDate:
    """_convert_date()内部関数のテスト."""

    def test_converts_without_cls(self) -> None:
        result = _convert_date("2024-01-15", None)
        assert isinstance(result, date)
        assert result == date(2024, 1, 15)

    def test_converts_with_date_cls(self) -> None:
        result = _convert_date("2024-01-15", date)
        assert isinstance(result, date)
        assert result == date(2024, 1, 15)

    def test_converts_to_datetime_with_datetime_cls(self) -> None:
        result = _convert_date("2024-01-15", datetime)
        assert isinstance(result, datetime)
        assert result.year == 2024
        assert result.month == 1
        assert result.day == 15
        assert result.hour == 0
        assert result.tzinfo == JST


class TestConvertDatetime:
    """_convert_datetime()内部関数のテスト."""

    def test_converts_without_cls_with_time(self) -> None:
        """時刻情報がある場合はdatetimeを返す."""
        result = _convert_datetime("2024-01-15T10:30:00", None)
        assert isinstance(result, datetime)
        assert result.hour == 10
        assert result.minute == 30

    def test_converts_without_cls_at_midnight(self) -> None:
        """00:00:00の場合はdateを返す."""
        result = _convert_datetime("2024-01-15T00:00:00", None)
        assert isinstance(result, date)
        assert not isinstance(result, datetime)
        assert result == date(2024, 1, 15)

    def test_converts_to_date_with_date_cls(self) -> None:
        result = _convert_datetime("2024-01-15T10:30:00", date)
        assert isinstance(result, date)
        assert result == date(2024, 1, 15)

    def test_converts_with_datetime_cls(self) -> None:
        result = _convert_datetime("2024-01-15T10:30:00", datetime)
        assert isinstance(result, datetime)
        assert result.hour == 10
        assert result.minute == 30


class TestHasTime:
    """_has_time()関数のテスト."""

    def test_returns_true_for_datetime_with_hour(self) -> None:
        dt = datetime(2024, 1, 15, 10, 0, 0)
        assert _has_time(dt) is True

    def test_returns_true_for_datetime_with_minute(self) -> None:
        dt = datetime(2024, 1, 15, 0, 15, 0)
        assert _has_time(dt) is True

    def test_returns_true_for_datetime_with_second(self) -> None:
        dt = datetime(2024, 1, 15, 0, 0, 30)
        assert _has_time(dt) is True

    def test_returns_false_for_midnight(self) -> None:
        dt = datetime(2024, 1, 15, 0, 0, 0)
        assert _has_time(dt) is False

"""日付・時刻ユーティリティモジュール.

JST(日本標準時)での日時操作と、文字列からのdate/datetime変換機能を提供する。
"""

from datetime import date, datetime, timedelta, timezone

JST = timezone(timedelta(hours=+9), "JST")

LENGTH_DATE = 10  # "YYYY-MM-DD"


class DateType:
    """ISO形式の日付文字列の種類を判定するユーティリティクラス.

    文字列が日付のみ(YYYY-MM-DD)か、日時(datetime)形式かを判定する。
    """

    DATE = "date"
    DATETIME = "datetime"
    NONE = "none"

    @staticmethod
    def get_datetype(value: str) -> str:
        """文字列からDateTypeを判定する.

        Args:
            value: 判定対象の文字列

        Returns:
            DateType.DATE: YYYY-MM-DD形式の場合
            DateType.DATETIME: ISO datetime形式の場合
            DateType.NONE: どちらでもない場合

        Examples:
            >>> DateType.get_datetype("2024-01-15")
            'date'
            >>> DateType.get_datetype("2024-01-15T10:30:00")
            'datetime'
            >>> DateType.get_datetype("invalid")
            'none'
        """
        try:
            if len(value) == LENGTH_DATE:
                date.fromisoformat(value)
                return DateType.DATE
            datetime.fromisoformat(value)
            return DateType.DATETIME
        except ValueError:
            return DateType.NONE


def jst_now() -> datetime:
    """現在のJST日時を取得する.

    Returns:
        JSTタイムゾーン付きの現在日時
    """
    return datetime.now(JST)


def jst_today_datetime() -> datetime:
    """本日のJST 00:00:00を取得する.

    Returns:
        本日の0時0分0秒(JSTタイムゾーン付き)
    """
    return jst_now().replace(hour=0, minute=0, second=0, microsecond=0)


def jst_today(is_previous_day_until_2am: bool | None = None) -> date:
    """JSTでの本日の日付を取得する.

    Args:
        is_previous_day_until_2am: Trueの場合、午前2時までは前日として扱う

    Returns:
        本日の日付(is_previous_day_until_2am=Trueで午前2時前の場合は前日)

    Examples:
        >>> jst_today()  # 通常の今日の日付
        datetime.date(2024, 1, 15)
        >>> jst_today(is_previous_day_until_2am=True)  # 深夜1時の場合は前日
        datetime.date(2024, 1, 14)
    """
    now = jst_now()
    if is_previous_day_until_2am:
        return now.date() - timedelta(days=1) if now.hour < 2 else now.date()
    return now.date()


def jst_tomorrow() -> datetime:
    """明日のJST 00:00:00を取得する.

    Returns:
        明日の0時0分0秒(JSTタイムゾーン付き)
    """
    return jst_today_datetime() + timedelta(days=1)


# 後方互換性のためのエイリアス(非推奨)
jst_tommorow = jst_tomorrow


def convert_to_date_or_datetime(
    value: str | None, cls: type[date] | type[datetime] | None = None
) -> date | datetime | None:
    """ISO形式の文字列をdateまたはdatetimeに変換する.

    Args:
        value: ISO形式の日付または日時文字列(Noneも可)
        cls: 変換先の型(dateまたはdatetime)。Noneの場合は文字列から推測

    Returns:
        変換されたdate/datetimeオブジェクト、または変換できない場合はNone

    Examples:
        >>> convert_to_date_or_datetime("2024-01-15")
        datetime.date(2024, 1, 15)
        >>> convert_to_date_or_datetime("2024-01-15", datetime)
        datetime.datetime(2024, 1, 15, 0, 0, tzinfo=...)
        >>> convert_to_date_or_datetime("2024-01-15T10:30:00", date)
        datetime.date(2024, 1, 15)
    """
    if value is None:
        return None
    date_type = DateType.get_datetype(value)
    if date_type == DateType.DATE:
        return _convert_date(value, cls)
    if date_type == DateType.DATETIME:
        return _convert_datetime(value, cls)
    return None


def _convert_date(value: str, cls: type[date] | type[datetime] | None) -> date | datetime:
    """日付文字列をdate/datetimeに変換する(内部関数).

    Args:
        value: YYYY-MM-DD形式の文字列
        cls: 変換先の型

    Returns:
        dateまたはdatetimeオブジェクト
    """
    parsed_date = date.fromisoformat(value)
    if cls is None or cls is date:
        return parsed_date
    # cls is datetime
    return datetime(parsed_date.year, parsed_date.month, parsed_date.day, tzinfo=JST)


def _convert_datetime(value: str, cls: type[date] | type[datetime] | None) -> date | datetime:
    """日時文字列をdate/datetimeに変換する(内部関数).

    Args:
        value: ISO datetime形式の文字列
        cls: 変換先の型

    Returns:
        dateまたはdatetimeオブジェクト
    """
    parsed_datetime = datetime.fromisoformat(value)
    if cls is date:
        return parsed_datetime.date()
    if cls is datetime:
        return parsed_datetime
    # cls is None: 時刻情報がある場合はdatetime、ない場合はdate
    if _has_time(parsed_datetime):
        return parsed_datetime
    return parsed_datetime.date()


def _has_time(value: datetime) -> bool:
    """datetimeに時刻情報(0時0分0秒以外)があるか判定する.

    Args:
        value: 判定対象のdatetime

    Returns:
        時・分・秒のいずれかが0でない場合True

    Examples:
        >>> _has_time(datetime(2024, 1, 15, 10, 30, 0))
        True
        >>> _has_time(datetime(2024, 1, 15, 0, 0, 0))
        False
    """
    return value.hour != 0 or value.minute != 0 or value.second != 0

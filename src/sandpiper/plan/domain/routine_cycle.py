from datetime import date, timedelta
from enum import Enum

MONTHLY_OVERFLOW = 13
SUNDAY = 6
MONDAY = 0
TUESDAY = 1
THURSDAY = 3
FRIDAY = 4


def add_a_month(date: date) -> tuple[int, int]:
    """指定された日付の翌月の年月を取得する.

    Args:
        date: 基準となる日付

    Returns:
        翌月の(年, 月)のタプル

    Examples:
        >>> add_a_month(date(2024, 12, 15))
        (2025, 1)
        >>> add_a_month(date(2024, 3, 10))
        (2024, 4)
    """
    month = date.month + 1
    if month == MONTHLY_OVERFLOW:
        return date.year + 1, 1
    return date.year, month


def get_first_friday(year: int, month: int) -> date:
    """指定された年月の第1金曜日を取得する.

    Args:
        year: 年
        month: 月

    Returns:
        第1金曜日のdate

    Raises:
        ValueError: 第1金曜日が見つからない場合

    Examples:
        >>> get_first_friday(2024, 3)
        datetime.date(2024, 3, 1)
    """
    for day in range(1, 8):
        date_ = date(year=year, month=month, day=day)
        if date_.weekday() == FRIDAY:
            return date_
    raise ValueError("First Friday not found")


def get_third_friday(year: int, month: int) -> date:
    """指定された年月の第3金曜日を取得する.

    Args:
        year: 年
        month: 月

    Returns:
        第3金曜日のdate

    Raises:
        ValueError: 第1金曜日が見つからない場合(get_first_fridayから)

    Examples:
        >>> get_third_friday(2024, 3)
        datetime.date(2024, 3, 15)
    """
    first_friday = get_first_friday(year, month)
    return first_friday + timedelta(days=14)


def get_first_thursday(year: int, month: int) -> date:
    """指定された年月の第1木曜日を取得する.

    Args:
        year: 年
        month: 月

    Returns:
        第1木曜日のdate

    Raises:
        ValueError: 第1木曜日が見つからない場合

    Examples:
        >>> get_first_thursday(2024, 3)
        datetime.date(2024, 3, 7)
    """
    for day in range(1, 8):
        date_ = date(year=year, month=month, day=day)
        if date_.weekday() == THURSDAY:
            return date_
    raise ValueError("First Thursday not found")


def get_third_thursday(year: int, month: int) -> date:
    """指定された年月の第3木曜日を取得する.

    Args:
        year: 年
        month: 月

    Returns:
        第3木曜日のdate

    Raises:
        ValueError: 第1木曜日が見つからない場合(get_first_thursdayから)

    Examples:
        >>> get_third_thursday(2024, 3)
        datetime.date(2024, 3, 21)
    """
    first_thursday = get_first_thursday(year, month)
    return first_thursday + timedelta(days=14)


class RoutineCycle(Enum):
    """ルーチンタスクの実行タイミングを定義する列挙型.

    各値は日本語の説明文字列を持ち、next_dateメソッドで次回実行日を計算する。
    """

    DAILY = "毎日"
    WEEKLY_SUN = "毎週日"
    WEEKLY_MON = "毎週月"
    WEEKLY_TUE = "毎週火"
    WEEKLY_TUE_FRI = "毎週火・金"
    WEEKLY_WED = "毎週水"
    WEEKLY_THU = "毎週木"
    WEEKLY_FRI = "毎週金"
    WEEKLY_SAT = "毎週土"
    AFTER_3_DAYS = "3日後"
    AFTER_7_DAYS = "7日後"
    NEXT_WEEK = "翌週"
    MONTHLY_1ST = "毎月1日"
    MONTHLY_2ND = "毎月2日"
    MONTH_END = "月末"
    AFTER_20_DAYS = "20日後"
    MONTHLY_25TH = "毎月25日"
    FIRST_THIRD_FRI = "第1・3金"
    FIRST_THIRD_THU = "第1・3木"

    def next_date(self, basis_date: date) -> date:
        """基準日からタスクの次回予定日を計算する.

        Args:
            basis_date: 基準となる日付

        Returns:
            次回実行予定日

        Raises:
            ValueError: 不明なRoutineCycleの場合

        Examples:
            >>> RoutineCycle.DAILY.next_date(date(2024, 3, 20))
            datetime.date(2024, 3, 20)
            >>> RoutineCycle.MONTHLY_1ST.next_date(date(2024, 3, 20))
            datetime.date(2024, 4, 1)
        """
        weekday = basis_date.weekday()
        match self:
            case RoutineCycle.DAILY:
                return basis_date + timedelta(days=1)
            case RoutineCycle.WEEKLY_SUN:
                days_until_sun = (SUNDAY - weekday) % 7
                if days_until_sun == 0:  # 日曜日の場合は次の日曜日へ
                    return basis_date + timedelta(days=7)
                return basis_date + timedelta(days=days_until_sun)
            case RoutineCycle.WEEKLY_MON:
                days_until_mon = (MONDAY - weekday) % 7
                if days_until_mon == 0:  # 月曜日の場合は次の月曜日へ
                    return basis_date + timedelta(days=7)
                return basis_date + timedelta(days=days_until_mon)
            case RoutineCycle.WEEKLY_TUE:
                days_until_tue = (TUESDAY - weekday) % 7
                if days_until_tue == 0:  # 火曜日の場合は次の火曜日へ
                    return basis_date + timedelta(days=7)
                return basis_date + timedelta(days=days_until_tue)
            case RoutineCycle.WEEKLY_TUE_FRI:
                if weekday == 1:  # 火曜日の場合は金曜日へ
                    return basis_date + timedelta(days=3)
                if weekday in [2, 3]:  # 水・木曜日の場合は金曜日へ
                    return basis_date + timedelta(days=(4 - weekday))
                if weekday == 4:  # 金曜日の場合は次の火曜日へ
                    return basis_date + timedelta(days=4)
                # 土日月の場合は次の火曜日へ
                return basis_date + timedelta(days=(8 - weekday) % 7)
            case RoutineCycle.WEEKLY_WED:
                days_until_wed = (2 - weekday) % 7
                if days_until_wed == 0:  # 水曜日の場合は次の水曜日へ
                    return basis_date + timedelta(days=7)
                return basis_date + timedelta(days=days_until_wed)
            case RoutineCycle.WEEKLY_THU:
                days_until_thu = (THURSDAY - weekday) % 7
                if days_until_thu == 0:  # 木曜日の場合は次の木曜日へ
                    return basis_date + timedelta(days=7)
                return basis_date + timedelta(days=days_until_thu)
            case RoutineCycle.WEEKLY_FRI:
                days_until_fri = (FRIDAY - weekday) % 7
                if days_until_fri == 0:  # 金曜日の場合は次の金曜日へ
                    return basis_date + timedelta(days=7)
                return basis_date + timedelta(days=days_until_fri)
            case RoutineCycle.WEEKLY_SAT:
                days_until_sat = (5 - weekday) % 7
                if days_until_sat == 0:  # 土曜日の場合は次の土曜日へ
                    return basis_date + timedelta(days=7)
                return basis_date + timedelta(days=days_until_sat)
            case RoutineCycle.AFTER_3_DAYS:
                return basis_date + timedelta(days=3)
            case RoutineCycle.AFTER_7_DAYS:
                return basis_date + timedelta(days=7)
            case RoutineCycle.NEXT_WEEK:
                return basis_date + timedelta(days=7)
            case RoutineCycle.MONTHLY_1ST:
                year, month = add_a_month(basis_date)
                return date(year=year, month=month, day=1)
            case RoutineCycle.MONTHLY_2ND:
                date_ = basis_date.replace(day=2)
                if basis_date < date_:
                    return date_
                year, month = add_a_month(basis_date)
                return date(year=year, month=month, day=2)
            case RoutineCycle.MONTH_END:
                month = basis_date.month + 1
                if month == MONTHLY_OVERFLOW:
                    return basis_date.replace(year=basis_date.year + 1, month=1, day=1) - timedelta(days=1)
                return basis_date.replace(month=month, day=1) - timedelta(days=1)
            case RoutineCycle.AFTER_20_DAYS:
                return basis_date + timedelta(days=20)
            case RoutineCycle.MONTHLY_25TH:
                date_ = basis_date.replace(day=25)
                if basis_date < date_:
                    return date_
                year, month = add_a_month(basis_date)
                return date(year=year, month=month, day=25)
            case RoutineCycle.FIRST_THIRD_FRI:
                first_friday = get_first_friday(basis_date.year, basis_date.month)
                if basis_date < first_friday:
                    return first_friday
                third_friday = get_third_friday(basis_date.year, basis_date.month)
                if basis_date < third_friday:
                    return third_friday
                if basis_date == third_friday:  # 第3金曜日の場合は翌月の第1金曜日へ
                    year, month = add_a_month(basis_date)
                    return get_first_friday(year, month)
                year, month = add_a_month(basis_date)
                return get_first_friday(year, month)
            case RoutineCycle.FIRST_THIRD_THU:
                first_thursday = get_first_thursday(basis_date.year, basis_date.month)
                if basis_date < first_thursday:
                    return first_thursday
                third_thursday = get_third_thursday(basis_date.year, basis_date.month)
                if basis_date < third_thursday:
                    return third_thursday
                year, month = add_a_month(basis_date)
                return get_first_thursday(year, month)

    @staticmethod
    def from_text(text: str) -> "RoutineCycle":
        """文字列からRoutineCycleを取得する.

        Args:
            text: RoutineCycleの値文字列

        Returns:
            対応するRoutineCycle

        Raises:
            ValueError: 対応するRoutineCycleが見つからない場合

        Examples:
            >>> RoutineCycle.from_text("毎日")
            <RoutineCycle.DAILY: '毎日'>
            >>> RoutineCycle.from_text("第1・3木")
            <RoutineCycle.FIRST_THIRD_THU: '第1・3木'>
        """
        for routine_cycle in RoutineCycle:
            if routine_cycle.value == text:
                return routine_cycle
        msg = f"RoutineCycle not found: {text}"
        raise ValueError(msg)

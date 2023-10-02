"""Util methods to build fields of Pull Request objects"""
import re
from datetime import date, datetime, time
from codereview.time_ranges import TimeRanges


def get_author_id_from_author_full_name(author_full_name: str) -> str:
    """get author id from a string with full name and author id

    Args:
        author_full_name (str): Kathe Maria Ruiz (T99999)

    Returns:
        str: T99999
    """
    author_full_name_len = len(author_full_name)
    return author_full_name[author_full_name_len - 7: author_full_name_len - 1].upper()


def get_author_full_name(author_full_name: str) -> str:
    if len(author_full_name):
        author_name = author_full_name.split('-')[0]
        author_name = re.sub('\(.+?\)', '', author_name)

        return author_name
    return ''


def get_author_with_prefix(author_id: str):
    """get author id with prefix 0"""
    return "0" + author_id.upper()


def date_to_datetime(current_date: str):
    """convert date to datetime"""
    return datetime.strptime(current_date, "%d/%m/%Y %H:%M:%S")


def date_to_timestamp(current_date: str) -> float:
    """convert date to timestamp"""
    return date_to_datetime(current_date).timestamp()


def get_diff_of_dates(start_date: str, end_date: str) -> float:
    """get the difference between two dates in timestamp format"""
    start_date_in_timestamp = date_to_timestamp(start_date)
    end_date_in_timestamp = date_to_timestamp(end_date)

    return end_date_in_timestamp - start_date_in_timestamp


def get_diff_of_dates_in_minutes(start_date: str, end_date: str):
    """get the difference between two dates in minutes"""
    return get_diff_of_dates(start_date, end_date) / 60


def get_diff_of_dates_in_hours(start_date: str, end_date: str):
    """get the difference between two dates in hours"""
    return get_diff_of_dates(start_date, end_date) / (60 * 60)


def get_days_between_dates(start_date: str, end_date: str) -> int:
    """get the number of days between dates"""
    return (
            date_to_datetime(end_date).date() - date_to_datetime(start_date).date()
    ).days


def is_time_in_range(check_time: time, time_range: TimeRanges) -> bool:
    """check if the time is in the time range"""
    return time_range.start_time <= check_time <= time_range.end_time


def get_time_range(current_date: str) -> TimeRanges:
    """get the time range the current_date belongs to
    A: 00:00:00 am - 07:29:59 am
    B: 07:30:00 am - 08:59:59 am
    C: 09:00:00 am - 05:59:59 pm
    D: 06:00:00 pm - 11:59:59 pm
    """
    current_time = date_to_datetime(current_date).time()

    if is_time_in_range(
            current_time,
            TimeRanges.A,
    ):
        return TimeRanges.A

    if is_time_in_range(
            current_time,
            TimeRanges.B,
    ):
        return TimeRanges.B

    if is_time_in_range(
            current_time,
            TimeRanges.C,
    ):
        return TimeRanges.C

    return TimeRanges.D


def get_diff_of_times_in_hours(start_time: time, end_time: time):
    """get difference between two times in hours"""
    return (
                   datetime.combine(date.min, end_time) - datetime.combine(date.min, start_time)
           ).total_seconds() / (60 * 60)


def get_time_in_hours_with_open_time_in_range_a(
        open_time: time,
        close_date_hour_range: TimeRanges,
        days_between_dates: int,
        diff_dates_in_hours: float,
) -> float:
    """get time in hours when open time is in range A"""

    time_to_end_of_range = get_diff_of_times_in_hours(
        open_time, TimeRanges.B.start_time
    )

    if close_date_hour_range == TimeRanges.A:
        if days_between_dates == 0:
            return diff_dates_in_hours
        if days_between_dates >= 1:
            return (
                    diff_dates_in_hours
                    - (time_to_end_of_range)
                    - TimeRanges.B.hours
                    - (
                            (days_between_dates - 1)
                            * (TimeRanges.D.hours + TimeRanges.A.hours + TimeRanges.B.hours)
                    )
            )
    elif close_date_hour_range == TimeRanges.B:
        return (
                diff_dates_in_hours
                - (time_to_end_of_range)
                - (
                        (TimeRanges.B.hours + TimeRanges.D.hours + TimeRanges.A.hours)
                        * days_between_dates
                )
        )

    return (
            diff_dates_in_hours
            - (time_to_end_of_range)
            - TimeRanges.B.hours
            - (
                    (TimeRanges.D.hours + TimeRanges.A.hours + TimeRanges.B.hours)
                    * days_between_dates
            )
    )


def get_time_in_hours_with_open_time_in_range_b(
        open_time: time,
        close_date_hour_range: TimeRanges,
        days_between_dates: int,
        diff_dates_in_hours: float,
) -> float:
    """get time in hours when open time is in range B"""
    time_to_end_of_range = get_diff_of_times_in_hours(
        open_time, TimeRanges.C.start_time
    )

    if close_date_hour_range == TimeRanges.A:
        return (
                diff_dates_in_hours
                - time_to_end_of_range
                - (
                        (TimeRanges.D.hours + TimeRanges.A.hours + TimeRanges.B.hours)
                        * (days_between_dates - 1)
                )
        )
    if close_date_hour_range == TimeRanges.B:
        if days_between_dates == 0:
            return diff_dates_in_hours
        if days_between_dates >= 1:
            return (
                    diff_dates_in_hours
                    - time_to_end_of_range
                    - TimeRanges.D.hours
                    - TimeRanges.A.hours
                    - (
                            (TimeRanges.B.hours + TimeRanges.D.hours + TimeRanges.A.hours)
                            * (days_between_dates - 1)
                    )
            )
    return (
            diff_dates_in_hours
            - time_to_end_of_range
            - (
                    (TimeRanges.D.hours + TimeRanges.A.hours + TimeRanges.B.hours)
                    * days_between_dates
            )
    )


def get_time_in_hours_with_open_time_in_range_c(
        close_date_hour_range: TimeRanges,
        days_between_dates: int,
        diff_dates_in_hours: float,
) -> float:
    """get time in hours when open time is in range C"""
    if close_date_hour_range == TimeRanges.A:
        return diff_dates_in_hours - (
                (TimeRanges.D.hours + TimeRanges.A.hours + TimeRanges.B.hours)
                * (days_between_dates - 1)
        )
    if close_date_hour_range == TimeRanges.B:
        return (
                diff_dates_in_hours
                - TimeRanges.D.hours
                - TimeRanges.A.hours
                - (
                        (TimeRanges.B.hours + TimeRanges.D.hours + TimeRanges.A.hours)
                        * (days_between_dates - 1)
                )
        )

    if close_date_hour_range == TimeRanges.C and days_between_dates == 0:
        return diff_dates_in_hours

    return diff_dates_in_hours - (
            (TimeRanges.D.hours + TimeRanges.A.hours + TimeRanges.B.hours)
            * days_between_dates
    )


def get_time_in_hours_with_open_time_in_range_d(
        open_time: time,
        close_date_hour_range: TimeRanges,
        days_between_dates: int,
        diff_dates_in_hours: float,
) -> float:
    """get time in hours when open time is in range D"""
    time_to_end_of_range = get_diff_of_times_in_hours(open_time, TimeRanges.D.end_time)

    if close_date_hour_range == TimeRanges.A:
        return (
                diff_dates_in_hours
                - time_to_end_of_range
                - (
                        (TimeRanges.A.hours + TimeRanges.B.hours + TimeRanges.D.hours)
                        * (days_between_dates - 1)
                )
        )
    if close_date_hour_range == TimeRanges.B:
        return (
                diff_dates_in_hours
                - time_to_end_of_range
                - TimeRanges.A.hours
                - (
                        (TimeRanges.B.hours + TimeRanges.D.hours + TimeRanges.A.hours)
                        * (days_between_dates - 1)
                )
        )

    if close_date_hour_range == TimeRanges.D and days_between_dates == 0:
        return diff_dates_in_hours

    return (
            diff_dates_in_hours
            - time_to_end_of_range
            - TimeRanges.A.hours
            - TimeRanges.B.hours
            - (
                    (TimeRanges.D.hours + TimeRanges.A.hours + TimeRanges.B.hours)
                    * (days_between_dates - 1)
            )
    )


def get_diff_of_dates_in_hours_without_out_of_office_hours(
        start_date: str, end_date: str, diff_dates_in_hours: float
):
    """get the difference between two dates in hours without out of office hours"""
    open_date_hour_range = get_time_range(start_date)
    close_date_hour_range = get_time_range(end_date)

    open_date = date_to_datetime(start_date)

    days_between_dates = get_days_between_dates(start_date, end_date)

    if open_date_hour_range == TimeRanges.A:
        return get_time_in_hours_with_open_time_in_range_a(
            open_date.time(),
            close_date_hour_range,
            days_between_dates,
            diff_dates_in_hours,
        )

    if open_date_hour_range == TimeRanges.B:
        return get_time_in_hours_with_open_time_in_range_b(
            open_date.time(),
            close_date_hour_range,
            days_between_dates,
            diff_dates_in_hours,
        )
    if open_date_hour_range == TimeRanges.C:
        return get_time_in_hours_with_open_time_in_range_c(
            close_date_hour_range,
            days_between_dates,
            diff_dates_in_hours,
        )

    return get_time_in_hours_with_open_time_in_range_d(
        open_date.time(),
        close_date_hour_range,
        days_between_dates,
        diff_dates_in_hours,
    )


def get_type_of_commit(commit_message: str, file_count: int) -> str:
    """get the type of the commit
    - devops
    - feat
    - fix
    - perf
    - refactor
    - test
    - style
    - chore
    - ci
    - docs
    - other"""

    if (
            "MERGE" in commit_message.upper() and file_count == 0
    ) or "[CI-RELEASE" in commit_message.upper():
        return "devops"

    if (
            "FEAT:" in commit_message.upper()
            or "FEAT(" in commit_message.upper()
            or "FEAT (" in commit_message.upper()
    ):
        return "feat"

    if "FIX:" in commit_message.upper() or "FIX(" in commit_message.upper():
        return "fix"

    if "PERF:" in commit_message.upper() or "PERF(" in commit_message.upper():
        return "perf"

    if "REFACTOR:" in commit_message.upper() or "REFACTOR(" in commit_message.upper():
        return "refactor"

    if "TEST:" in commit_message.upper() or "TEST(" in commit_message.upper():
        return "test"

    if "STYLE:" in commit_message.upper() or "STYLE(" in commit_message.upper():
        return "style"

    if "CHORE:" in commit_message.upper() or "CHORE(" in commit_message.upper():
        return "chore"

    if (
            "CI:" in commit_message.upper()
            or "CI(" in commit_message.upper()
            or "CI (" in commit_message.upper()
    ):
        return "ci"

    if (
            "DOCS:" in commit_message.upper()
            or "DOCS(" in commit_message.upper()
            or "DOC:" in commit_message.upper()
            or "DOC(" in commit_message.upper()
    ):
        return "docs"

    return "other"


def extract_squad_id(squad_name):
    match_expr = re.search('\[(.+?)\]', squad_name)
    if match_expr:
        return match_expr.group(1)
    else:
        return ''


def current_date_formated():
    current_date = datetime.now()
    return str(current_date.day) + "/" + str(current_date.month) + "/" + str(current_date.year)


def first_day_custom_date(month: str, year: str):
    return '01' + '/' + str(month) + '/' + str(year)

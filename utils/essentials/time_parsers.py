import re
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from utils.db.timezone_db import is_valid_timezone


# 🌸───────────────────────────────────────────────🌸
#         ⏰ Reminder Time String → Unix
# 🌸───────────────────────────────────────────────🌸
def parse_remind_on(value: str, tz_str: str) -> tuple[bool, int | None, str | None]:
    """
    Convert remind_on string into Unix timestamp (seconds) using user's timezone.

    Args:
        value: input string like "12/30 18:20" or "1d12h30m"
        tz_str: timezone string, e.g. "Asia/Manila"

    Returns:
        (success, timestamp, error_message)
        - success: bool
        - timestamp: int (unix seconds) if success else None
        - error_message: str if failed else None
    """
    try:
        tz = ZoneInfo(tz_str)
    except Exception:
        return False, None, f"Invalid timezone: {tz_str}"

    now = datetime.now(tz)

    # ──────────────────────────────
    # Case 1: Absolute date M/D HH:MM
    # ──────────────────────────────
    abs_date_match = re.match(r"^(\d{1,2})/(\d{1,2})\s+(\d{1,2}):(\d{2})$", value)
    if abs_date_match:
        month, day, hour, minute = map(int, abs_date_match.groups())

        if not (1 <= month <= 12):
            return False, None, f"Invalid month: {month}"
        if not (0 <= hour <= 23):
            return False, None, f"Invalid hour: {hour}"
        if not (0 <= minute <= 59):
            return False, None, f"Invalid minute: {minute}"

        try:
            target = datetime(now.year, month, day, hour, minute, tzinfo=tz)
        except ValueError:
            return False, None, f"Invalid date: {month}/{day}"

        # If date already passed this year, push to next year
        if target <= now:
            target = datetime(now.year + 1, month, day, hour, minute, tzinfo=tz)

        return True, int(target.timestamp()), None

    # ──────────────────────────────
    # Case 2: Relative format (XdYhZm)
    # ──────────────────────────────
    rel_pattern = re.compile(
        r"^(?:(?P<days>\d+)d)?(?:(?P<hours>\d+)h)?(?:(?P<minutes>\d+)m)?$"
    )
    rel_match = rel_pattern.match(value.strip().lower())
    if rel_match:
        days = int(rel_match.group("days") or 0)
        hours = int(rel_match.group("hours") or 0)
        minutes = int(rel_match.group("minutes") or 0)

        if days == hours == minutes == 0:
            return False, None, "Relative time must not be zero"

        delta = timedelta(days=days, hours=hours, minutes=minutes)
        target = now + delta
        return True, int(target.timestamp()), None

    # ──────────────────────────────
    # Invalid format
    # ──────────────────────────────
    return False, None, f"Invalid remind_on format: {value}"


# 🌸───────────────────────────────────────────────🌸
#         ⏰ Convert Duration String → Seconds
# 🌸───────────────────────────────────────────────🌸
import re
from datetime import timedelta


def convert_duration_to_seconds(value: str) -> tuple[bool, int | None, str | None]:
    """
    Convert a duration string into seconds.

    Args:
        value: input string like "1d12h30m" or "3h"

    Returns:
        (success, total_seconds, error_message)
        - success: bool
        - total_seconds: int if success else None
        - error_message: str if failed else None
    """
    # Match relative duration format
    rel_pattern = re.compile(
        r"^(?:(?P<days>\d+)d)?(?:(?P<hours>\d+)h)?(?:(?P<minutes>\d+)m)?$"
    )
    rel_match = rel_pattern.match(value.strip().lower())
    if rel_match:
        days = int(rel_match.group("days") or 0)
        hours = int(rel_match.group("hours") or 0)
        minutes = int(rel_match.group("minutes") or 0)

        if days == hours == minutes == 0:
            return False, None, "Duration must not be zero"

        delta = timedelta(days=days, hours=hours, minutes=minutes)
        return True, int(delta.total_seconds()), None

    return False, None, f"Invalid duration format: {value}"


# 🌸───────────────────────────────────────────────🌸
#       ⏰ Seconds → Human-readable time helper
# 🌸───────────────────────────────────────────────🌸
def format_display_duration(seconds: int, compact: bool = False) -> str:
    """
    Convert seconds into human-readable duration.

    Parameters:
    - seconds: total seconds
    - compact: if True, returns short form like '1d30m', else '1 day 30 minutes'

    Returns:
    - str
    """
    intervals = (
        ("month", 30 * 24 * 60 * 60),
        ("week", 7 * 24 * 60 * 60),
        ("day", 24 * 60 * 60),
        ("hour", 60 * 60),
        ("minute", 60),
    )

    result = []

    for name, count in intervals:
        value = seconds // count
        if value:
            if compact:
                # short form like 1d, 2h, 30m
                result.append(f"{value}{name[0]}")
            else:
                # long form
                unit = name if value == 1 else f"{name}s"
                result.append(f"{value} {unit}")
            seconds -= value * count

    if not result:
        return "0 minutes" if not compact else "0m"

    return " ".join(result)


# 🌸───────────────────────────────────────────────🌸
#         ⏰ Repeat Interval String → Seconds
# 🌸───────────────────────────────────────────────🌸
def parse_repeat_interval(value: str) -> tuple[bool, int | str]:
    """
    Convert repeat_interval string into seconds.

    Supports relative time only:
      - "1d12h", "12h30m", "30m"

    Validates:
      - No absolute dates allowed
      - Must be at least 5 minutes
      - Proper formatting (XdYhZm)

    Returns:
      - (True, seconds) if valid
      - (False, error_message) if invalid
    """
    if not isinstance(value, str) or not value.strip():
        return False, "Repeat interval must be a string"

    value = value.strip().lower()

    # Reject absolute date formats (M/D HH:MM)
    if re.match(r"^\d{1,2}/\d{1,2}\s+\d{1,2}:\d{2}$", value):
        return False, "Repeat interval cannot be an absolute date"

    # Relative time pattern
    rel_pattern = re.compile(
        r"^(?:(?P<days>\d+)d)?" r"(?:(?P<hours>\d+)h)?" r"(?:(?P<minutes>\d+)m)?$"
    )
    rel_match = rel_pattern.match(value)
    if not rel_match:
        return False, f"Invalid repeat interval format: {value}"

    days = int(rel_match.group("days") or 0)
    hours = int(rel_match.group("hours") or 0)
    minutes = int(rel_match.group("minutes") or 0)

    total_seconds = days * 86400 + hours * 3600 + minutes * 60

    # Minimum 5 minutes
    if total_seconds < 300:
        return False, "Repeat interval must be at least 5 minutes"

    return True, total_seconds


# 🌸───────────────────────────────────────────────🌸
#       ⏰ Seconds → Human-readable time helper
# 🌸───────────────────────────────────────────────🌸
def format_repeats_on(seconds: int, compact: bool = False) -> str:
    """
    Convert seconds into human-readable duration.

    Parameters:
    - seconds: total seconds
    - compact: if True, returns short form like '1d30m', else '1 day 30 minutes'

    Returns:
    - str
    """
    intervals = (
        ("month", 30 * 24 * 60 * 60),
        ("week", 7 * 24 * 60 * 60),
        ("day", 24 * 60 * 60),
        ("hour", 60 * 60),
        ("minute", 60),
    )

    result = []

    for name, count in intervals:
        value = seconds // count
        if value:
            if compact:
                # short form like 1d, 2h, 30m
                result.append(f"{value}{name[0]}")
            else:
                # long form
                unit = name if value == 1 else f"{name}s"
                result.append(f"{value} {unit}")
            seconds -= value * count

    if not result:
        return "0 minutes" if not compact else "0m"

    return " ".join(result)




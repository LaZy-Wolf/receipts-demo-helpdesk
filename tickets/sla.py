"""SLA due dates in business hours."""
from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo

SLA_HOURS = {"urgent": 4, "high": 8, "medium": 24, "low": 72}


def _at(dt: datetime, t: time) -> datetime:
    return dt.replace(hour=t.hour, minute=t.minute, second=0, microsecond=0)


def _next_business_day(dt: datetime, day_start: time) -> datetime:
    dt = _at(dt + timedelta(days=1), day_start)
    while dt.weekday() >= 5:
        dt += timedelta(days=1)
    return dt


def into_business_hours(dt: datetime, day_start: time, day_end: time) -> datetime:
    """Move `dt` forward to the next moment inside business hours (or leave it if already inside)."""
    if dt.weekday() >= 5 or dt.time() >= day_end:
        return _next_business_day(dt, day_start)
    if dt.time() < day_start:
        return _at(dt, day_start)
    return dt


def add_business_hours(start: datetime, hours: float, day_start: time = time(9), day_end: time = time(17)) -> datetime:
    """Advance `start` by `hours`, counting only Monday-Friday between day_start and day_end.

    Works on the wall clock of `start`, so pass a datetime in the team's local time.
    """
    current = into_business_hours(start, day_start, day_end)
    remaining = timedelta(hours=hours)
    while True:
        available = _at(current, day_end) - current
        if remaining <= available:
            return current + remaining
        remaining -= available
        current = _next_business_day(current, day_start)


def due_at(team, priority: str, start: datetime) -> datetime:
    """UTC due date for a ticket of `priority` for `team`, starting at aware datetime `start`."""
    tz = ZoneInfo(team.timezone)
    local = start.astimezone(tz)
    return add_business_hours(local, SLA_HOURS[priority], team.day_start, team.day_end).astimezone(ZoneInfo("UTC"))

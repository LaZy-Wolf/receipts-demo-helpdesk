from datetime import datetime, time
from zoneinfo import ZoneInfo

from tickets.models import Team
from tickets.sla import add_business_hours, due_at

# 2026-06-01 is a Monday.


def test_within_one_day():
    assert add_business_hours(datetime(2026, 6, 1, 10, 0), 4) == datetime(2026, 6, 1, 14, 0)


def test_rolls_to_next_weekday():
    assert add_business_hours(datetime(2026, 6, 2, 15, 0), 4) == datetime(2026, 6, 3, 11, 0)


def test_before_hours_starts_at_opening():
    assert add_business_hours(datetime(2026, 6, 1, 7, 30), 2) == datetime(2026, 6, 1, 11, 0)


def test_after_hours_starts_next_morning():
    assert add_business_hours(datetime(2026, 6, 3, 18, 0), 1) == datetime(2026, 6, 4, 10, 0)


def test_created_on_saturday_starts_monday():
    assert add_business_hours(datetime(2026, 6, 6, 12, 0), 3) == datetime(2026, 6, 8, 12, 0)


def test_custom_hours():
    assert add_business_hours(datetime(2026, 6, 1, 8, 0), 2, time(8), time(12)) == datetime(2026, 6, 1, 10, 0)


def test_due_at_uses_team_timezone():
    team = Team(name="EU", timezone="Europe/Berlin")
    start = datetime(2026, 6, 1, 6, 0, tzinfo=ZoneInfo("UTC"))  # 08:00 in Berlin, before opening
    assert due_at(team, "urgent", start) == datetime(2026, 6, 1, 11, 0, tzinfo=ZoneInfo("UTC"))

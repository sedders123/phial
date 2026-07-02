"""Test Schedule class."""

from datetime import UTC, datetime, timedelta
from zoneinfo import ZoneInfo

import pytest
from freezegun import freeze_time

from phial.scheduler import Schedule


def test_day() -> None:
    """Test day function correctly adds a day."""
    schedule = Schedule().every().day()
    now = datetime.now(tz=UTC)
    next_run = schedule.get_next_run_time(now)
    expected_datetime = now + timedelta(days=1)
    assert next_run == expected_datetime


def test_days() -> None:
    """Test days function correctly adds days."""
    schedule = Schedule().every().days(2)
    now = datetime.now(tz=UTC)
    next_run = schedule.get_next_run_time(now)
    expected_datetime = now + timedelta(days=2)
    assert next_run == expected_datetime


def test_hour() -> None:
    """Test hour function correctly adds an hour."""
    schedule = Schedule().every().hour()
    now = datetime.now(tz=UTC)
    next_run = schedule.get_next_run_time(now)
    expected_datetime = now + timedelta(hours=1)
    assert next_run == expected_datetime


def test_hours() -> None:
    """Test hours function correctly adds hours."""
    schedule = Schedule().every().hours(2)
    now = datetime.now(tz=UTC)
    next_run = schedule.get_next_run_time(now)
    expected_datetime = now + timedelta(hours=2)
    assert next_run == expected_datetime


def test_minute() -> None:
    """Test minute function correctly adds a minute."""
    schedule = Schedule().every().minute()
    now = datetime.now(tz=UTC)
    next_run = schedule.get_next_run_time(now)
    expected_datetime = now + timedelta(minutes=1)
    assert next_run == expected_datetime


def test_minutes() -> None:
    """Test minutes function correctly adds minutes."""
    schedule = Schedule().every().minutes(2)
    now = datetime.now(tz=UTC)
    next_run = schedule.get_next_run_time(now)
    expected_datetime = now + timedelta(minutes=2)
    assert next_run == expected_datetime


def test_second() -> None:
    """Test second function correctly adds a second."""
    schedule = Schedule().every().second()
    now = datetime.now(tz=UTC)
    next_run = schedule.get_next_run_time(now)
    expected_datetime = now + timedelta(seconds=1)
    assert next_run == expected_datetime


def test_seconds() -> None:
    """Test seconds function correctly adds seconds."""
    schedule = Schedule().every().seconds(2)
    now = datetime.now(tz=UTC)
    next_run = schedule.get_next_run_time(now)
    expected_datetime = now + timedelta(seconds=2)
    assert next_run == expected_datetime


@freeze_time("2018-01-01 10:00:00")
def test_at_before_time() -> None:
    """Test at will run on the first day if time not already passed."""
    schedule = Schedule().every().day().at(12, 00)
    now = datetime.now(tz=UTC)
    next_run = schedule.get_next_run_time(now)
    expected_datetime = (now).replace(hour=12, minute=0, second=0, microsecond=0)
    assert next_run == expected_datetime


@freeze_time("2018-01-01 13:00:00")
def test_at_after_time() -> None:
    """Test at will run on the next day if time already passed."""
    schedule = Schedule().every().day().at(12, 00)
    now = datetime.now(tz=UTC)
    next_run = schedule.get_next_run_time(now)
    expected_datetime = (now + timedelta(days=1)).replace(
        hour=12,
        minute=0,
        second=0,
        microsecond=0,
    )
    assert next_run == expected_datetime


@freeze_time("2018-07-01 09:00:00")
def test_at_with_timezone_object() -> None:
    """Test at interprets the time of day in the provided timezone."""
    tz = ZoneInfo("Europe/London")
    schedule = Schedule().every().day().at(12, 00, tz=tz)
    now = datetime.now(tz=UTC)
    next_run = schedule.get_next_run_time(now)
    # 12:00 London (BST, UTC+1) == 11:00 UTC, which is after 09:00 UTC now.
    assert next_run == datetime(2018, 7, 1, 12, 0, tzinfo=tz)
    assert next_run == datetime(2018, 7, 1, 11, 0, tzinfo=UTC)


@freeze_time("2018-07-01 09:00:00")
def test_at_with_timezone_string() -> None:
    """Test at accepts an IANA timezone name and resolves it."""
    schedule = Schedule().every().day().at(12, 00, tz="Europe/London")
    now = datetime.now(tz=UTC)
    next_run = schedule.get_next_run_time(now)
    assert next_run == datetime(2018, 7, 1, 12, 0, tzinfo=ZoneInfo("Europe/London"))
    assert next_run == datetime(2018, 7, 1, 11, 0, tzinfo=UTC)


@freeze_time("2018-07-01 12:00:00")
def test_at_after_time_with_timezone() -> None:
    """Test at rolls to the next day when the zoned time has passed."""
    tz = ZoneInfo("Europe/London")
    schedule = Schedule().every().day().at(12, 00, tz=tz)
    now = datetime.now(tz=UTC)
    next_run = schedule.get_next_run_time(now)
    # 12:00 London (BST, UTC+1) == 11:00 UTC, before 12:00 UTC now, so roll to
    # the next day.
    assert next_run == datetime(2018, 7, 2, 12, 0, tzinfo=tz)


@freeze_time("2018-06-30 23:30:00")
def test_at_with_timezone_crosses_utc_date_boundary() -> None:
    """Test at anchors to the local date, not the UTC date."""
    tz = ZoneInfo("Europe/London")
    schedule = Schedule().every().day().at(12, 00, tz=tz)
    now = datetime.now(tz=UTC)
    next_run = schedule.get_next_run_time(now)
    # 23:30 UTC is 2018-07-01 00:30 in London (BST). The next 12:00 falls on the
    # London date (2018-07-01), even though it is still 2018-06-30 in UTC.
    assert next_run == datetime(2018, 7, 1, 12, 0, tzinfo=tz)


def test_at_ambiguous_dst_time_uses_first_occurrence() -> None:
    """Test at picks the first occurrence when the local time happens twice."""
    tz = ZoneInfo("Europe/London")
    # Clocks go back on 2018-10-28, so 01:00 London occurs twice:
    # 01:00 BST (00:00 UTC) then 01:00 GMT (01:00 UTC). last_run is the evening
    # before, so the daily roll-forward lands next_run on 2018-10-28 01:00.
    # This deliberately does not use freeze_time: freezegun's FakeDatetime
    # mishandles fold across timedelta arithmetic, whereas real datetime
    # resolves fold=0 to the first (earlier) occurrence.
    #
    # A datetime that lands in a DST fold is (by PEP 495) never cross-zone
    # equal to a single UTC instant, so assert on the resolved instant via
    # astimezone, which respects fold=0 -> the first (earlier) 01:00.
    schedule = Schedule().every().day().at(1, 00, tz=tz)
    last_run = datetime(2018, 10, 27, 20, 0, tzinfo=UTC)
    next_run = schedule.get_next_run_time(last_run)
    assert next_run.astimezone(UTC) == datetime(2018, 10, 28, 0, 0, tzinfo=UTC)


@freeze_time("2018-10-28 00:30:00")
def test_at_after_first_occurrence_advances_to_next_day() -> None:
    """Test at advances past the second occurrence of a repeated local time."""
    tz = ZoneInfo("Europe/London")
    # 00:30 UTC is 01:30 BST, after the first 01:00. The next run should be
    # the following day, so the second 01:00 (01:00 UTC) cannot trigger it.
    schedule = Schedule().every().day().at(1, 00, tz=tz)
    now = datetime.now(tz=UTC)
    next_run = schedule.get_next_run_time(now)
    assert next_run == datetime(2018, 10, 29, 1, 0, tzinfo=tz)


def test_at_throws_when_on_hour() -> None:
    """Test at will throw if called on hour."""
    with pytest.raises(ValueError):
        Schedule().every().hour().at(12, 00)


def test_at_throws_when_on_minute() -> None:
    """Test at will throw if called on minute."""
    with pytest.raises(ValueError):
        Schedule().every().minute().at(12, 00)


def test_at_throws_when_on_already_set() -> None:
    """Test at will throw if already set."""
    with pytest.raises(ValueError):
        Schedule().every().day().at(12, 00).at(12, 00)


def test_at_throws_when_not_on_day() -> None:
    """Test at will throw if not on day."""
    with pytest.raises(ValueError):
        Schedule().every().at(12, 00)

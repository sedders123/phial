"""Test Schedule class."""
from datetime import datetime, timedelta

import pytest  # type: ignore
from freezegun import freeze_time  # type: ignore

from phial.scheduler import Schedule


def test_day() -> None:
    """Test day function correctly adds a day."""
    schedule = Schedule().every().day()
    now = datetime.now()
    next_run = schedule.get_next_run_time(now)
    expected_datetime = now + timedelta(days=1)
    assert next_run == expected_datetime


def test_days() -> None:
    """Test days function correctly adds days."""
    schedule = Schedule().every().days(2)
    now = datetime.now()
    next_run = schedule.get_next_run_time(now)
    expected_datetime = now + timedelta(days=2)
    assert next_run == expected_datetime


def test_hour() -> None:
    """Test hour function correctly adds an hour."""
    schedule = Schedule().every().hour()
    now = datetime.now()
    next_run = schedule.get_next_run_time(now)
    expected_datetime = now + timedelta(hours=1)
    assert next_run == expected_datetime


def test_hours() -> None:
    """Test hours function correctly adds hours."""
    schedule = Schedule().every().hours(2)
    now = datetime.now()
    next_run = schedule.get_next_run_time(now)
    expected_datetime = now + timedelta(hours=2)
    assert next_run == expected_datetime


def test_minute() -> None:
    """Test minute function correctly adds a minute."""
    schedule = Schedule().every().minute()
    now = datetime.now()
    next_run = schedule.get_next_run_time(now)
    expected_datetime = now + timedelta(minutes=1)
    assert next_run == expected_datetime


def test_minutes() -> None:
    """Test minutes function correctly adds minutes."""
    schedule = Schedule().every().minutes(2)
    now = datetime.now()
    next_run = schedule.get_next_run_time(now)
    expected_datetime = now + timedelta(minutes=2)
    assert next_run == expected_datetime


def test_second() -> None:
    """Test second function correctly adds a second."""
    schedule = Schedule().every().second()
    now = datetime.now()
    next_run = schedule.get_next_run_time(now)
    expected_datetime = now + timedelta(seconds=1)
    assert next_run == expected_datetime


def test_seconds() -> None:
    """Test seconds function correctly adds seconds."""
    schedule = Schedule().every().seconds(2)
    now = datetime.now()
    next_run = schedule.get_next_run_time(now)
    expected_datetime = now + timedelta(seconds=2)
    assert next_run == expected_datetime


@freeze_time('2018-01-01 10:00:00')  # type: ignore
def test_at_before_time() -> None:
    """Test at will run on the first day if time not already passed."""
    schedule = Schedule().every().day().at(12, 00)
    now = datetime.now()
    next_run = schedule.get_next_run_time(now)
    expected_datetime = (now).replace(hour=12,
                                      minute=0,
                                      second=0,
                                      microsecond=0)
    assert next_run == expected_datetime


@freeze_time('2018-01-01 13:00:00')  # type: ignore
def test_at_after_time() -> None:
    """Test at will run on the next day if time already passed."""
    schedule = Schedule().every().day().at(12, 00)
    now = datetime.now()
    next_run = schedule.get_next_run_time(now)
    expected_datetime = (now + timedelta(days=1)).replace(hour=12,
                                                          minute=0,
                                                          second=0,
                                                          microsecond=0)
    assert next_run == expected_datetime


def test_at_throws_when_on_hour() -> None:
    """Test at will throw if called on hour."""
    with pytest.raises(Exception):
        Schedule().every().hour().at(12, 00)


def test_at_throws_when_on_minute() -> None:
    """Test at will throw if called on minute."""
    with pytest.raises(Exception):
        Schedule().every().minute().at(12, 00)


def test_at_throws_when_on_already_set() -> None:
    """Test at will throw if already set."""
    with pytest.raises(Exception):
        Schedule().every().day().at(12, 00).at(12, 00)


def test_at_throws_when_not_on_day() -> None:
    """Test at will throw if not on day."""
    with pytest.raises(Exception):
        Schedule().every().at(12, 00)

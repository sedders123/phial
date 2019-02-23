from datetime import datetime, timedelta
from freezegun import freeze_time  # type: ignore
from phial.scheduler import Schedule
import pytest  # type: ignore


def test_day() -> None:
    schedule = Schedule().every().day()
    now = datetime.now()
    next_run = schedule.get_next_run_time(now)
    expected_datetime = now + timedelta(days=1)
    assert next_run == expected_datetime


def test_days() -> None:
    schedule = Schedule().every().days(2)
    now = datetime.now()
    next_run = schedule.get_next_run_time(now)
    expected_datetime = now + timedelta(days=2)
    assert next_run == expected_datetime


def test_hour() -> None:
    schedule = Schedule().every().hour()
    now = datetime.now()
    next_run = schedule.get_next_run_time(now)
    expected_datetime = now + timedelta(hours=1)
    assert next_run == expected_datetime


def test_hours() -> None:
    schedule = Schedule().every().hours(2)
    now = datetime.now()
    next_run = schedule.get_next_run_time(now)
    expected_datetime = now + timedelta(hours=2)
    assert next_run == expected_datetime


def test_minute() -> None:
    schedule = Schedule().every().minute()
    now = datetime.now()
    next_run = schedule.get_next_run_time(now)
    expected_datetime = now + timedelta(minutes=1)
    assert next_run == expected_datetime


def test_minutes() -> None:
    schedule = Schedule().every().minutes(2)
    now = datetime.now()
    next_run = schedule.get_next_run_time(now)
    expected_datetime = now + timedelta(minutes=2)
    assert next_run == expected_datetime


def test_second() -> None:
    schedule = Schedule().every().second()
    now = datetime.now()
    next_run = schedule.get_next_run_time(now)
    expected_datetime = now + timedelta(seconds=1)
    assert next_run == expected_datetime


def test_seconds() -> None:
    schedule = Schedule().every().seconds(2)
    now = datetime.now()
    next_run = schedule.get_next_run_time(now)
    expected_datetime = now + timedelta(seconds=2)
    assert next_run == expected_datetime


@freeze_time('2018-01-01 10:00:00')  # type: ignore
def test_at_before_time() -> None:
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
    schedule = Schedule().every().day().at(12, 00)
    now = datetime.now()
    next_run = schedule.get_next_run_time(now)
    expected_datetime = (now + timedelta(days=1)).replace(hour=12,
                                                          minute=0,
                                                          second=0,
                                                          microsecond=0)
    assert next_run == expected_datetime


def test_at_throws_when_on_hour() -> None:
    with pytest.raises(Exception):
        Schedule().every().hour().at(12, 00)


def test_at_throws_when_on_minute() -> None:
    with pytest.raises(Exception):
        Schedule().every().minute().at(12, 00)


def test_at_throws_when_on_already_set() -> None:
    with pytest.raises(Exception):
        Schedule().every().day().at(12, 00).at(12, 00)


def test_at_throws_when_not_on_day() -> None:
    with pytest.raises(Exception):
        Schedule().every().at(12, 00)

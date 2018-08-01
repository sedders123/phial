import unittest
from datetime import datetime, timedelta
from phial.scheduler import Schedule


class TestSchedules(unittest.TestCase):
    def test_day(self):
        every = Schedule()
        schedule = every.day()
        now = datetime.now()
        next_run = schedule.get_next_run_time(now)
        expected_datetime = now + timedelta(days=1)
        assert next_run == expected_datetime

    def test_days(self):
        every = Schedule()
        schedule = every.days(2)
        now = datetime.now()
        next_run = schedule.get_next_run_time(now)
        expected_datetime = now + timedelta(days=2)
        assert next_run == expected_datetime

    def test_hour(self):
        every = Schedule()
        schedule = every.hour()
        now = datetime.now()
        next_run = schedule.get_next_run_time(now)
        expected_datetime = now + timedelta(hours=1)
        assert next_run == expected_datetime

    def test_hours(self):
        every = Schedule()
        schedule = every.hours(2)
        now = datetime.now()
        next_run = schedule.get_next_run_time(now)
        expected_datetime = now + timedelta(hours=2)
        assert next_run == expected_datetime

    def test_minute(self):
        every = Schedule()
        schedule = every.minute()
        now = datetime.now()
        next_run = schedule.get_next_run_time(now)
        expected_datetime = now + timedelta(minutes=1)
        assert next_run == expected_datetime

    def test_minutes(self):
        every = Schedule()
        schedule = every.minutes(2)
        now = datetime.now()
        next_run = schedule.get_next_run_time(now)
        expected_datetime = now + timedelta(minutes=2)
        assert next_run == expected_datetime

    def test_second(self):
        every = Schedule()
        schedule = every.second()
        now = datetime.now()
        next_run = schedule.get_next_run_time(now)
        expected_datetime = now + timedelta(seconds=1)
        assert next_run == expected_datetime

    def test_seconds(self):
        every = Schedule()
        schedule = every.seconds(2)
        now = datetime.now()
        next_run = schedule.get_next_run_time(now)
        expected_datetime = now + timedelta(seconds=2)
        assert next_run == expected_datetime

    def test_at(self):
        every = Schedule()
        schedule = every.day().at(12, 00)
        now = datetime.now()
        next_run = schedule.get_next_run_time(now)
        expected_datetime = (now + timedelta(days=1)).replace(hour=12,
                                                              minute=0,
                                                              second=0,
                                                              microsecond=0)
        print(next_run)
        print(expected_datetime)
        assert next_run == expected_datetime

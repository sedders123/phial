import unittest
from datetime import datetime, timedelta
from freezegun import freeze_time
from unittest.mock import MagicMock
from phial.scheduler import Scheduler, Schedule, ScheduledJob


class TestSchedules(unittest.TestCase):
    def test_day(self):
        schedule = Schedule().every().day()
        now = datetime.now()
        next_run = schedule.get_next_run_time(now)
        expected_datetime = now + timedelta(days=1)
        assert next_run == expected_datetime

    def test_days(self):
        schedule = Schedule().every().days(2)
        now = datetime.now()
        next_run = schedule.get_next_run_time(now)
        expected_datetime = now + timedelta(days=2)
        assert next_run == expected_datetime

    def test_hour(self):
        schedule = Schedule().every().hour()
        now = datetime.now()
        next_run = schedule.get_next_run_time(now)
        expected_datetime = now + timedelta(hours=1)
        assert next_run == expected_datetime

    def test_hours(self):
        schedule = Schedule().every().hours(2)
        now = datetime.now()
        next_run = schedule.get_next_run_time(now)
        expected_datetime = now + timedelta(hours=2)
        assert next_run == expected_datetime

    def test_minute(self):
        schedule = Schedule().every().minute()
        now = datetime.now()
        next_run = schedule.get_next_run_time(now)
        expected_datetime = now + timedelta(minutes=1)
        assert next_run == expected_datetime

    def test_minutes(self):
        schedule = Schedule().every().minutes(2)
        now = datetime.now()
        next_run = schedule.get_next_run_time(now)
        expected_datetime = now + timedelta(minutes=2)
        assert next_run == expected_datetime

    def test_second(self):
        schedule = Schedule().every().second()
        now = datetime.now()
        next_run = schedule.get_next_run_time(now)
        expected_datetime = now + timedelta(seconds=1)
        assert next_run == expected_datetime

    def test_seconds(self):
        schedule = Schedule().every().seconds(2)
        now = datetime.now()
        next_run = schedule.get_next_run_time(now)
        expected_datetime = now + timedelta(seconds=2)
        assert next_run == expected_datetime

    @freeze_time('2018-01-01 10:00:00')
    def test_at_before_time(self):
        schedule = Schedule().every().day().at(12, 00)
        now = datetime.now()
        next_run = schedule.get_next_run_time(now)
        expected_datetime = (now).replace(hour=12,
                                          minute=0,
                                          second=0,
                                          microsecond=0)
        assert next_run == expected_datetime

    @freeze_time('2018-01-01 13:00:00')
    def test_at_after_time(self):
        schedule = Schedule().every().day().at(12, 00)
        now = datetime.now()
        next_run = schedule.get_next_run_time(now)
        expected_datetime = (now + timedelta(days=1)).replace(hour=12,
                                                              minute=0,
                                                              second=0,
                                                              microsecond=0)
        assert next_run == expected_datetime

    def test_at_throws_when_on_hour(self):
        with self.assertRaises(Exception):
            Schedule().every().hour().at(12, 00)

    def test_at_throws_when_on_minute(self):
        with self.assertRaises(Exception):
            Schedule().every().minute().at(12, 00)

    def test_at_throws_when_on_already_set(self):
        with self.assertRaises(Exception):
            Schedule().every().day().at(12, 00).at(12, 00)

    def test_at_throws_when_not_on_day(self):
        with self.assertRaises(Exception):
            Schedule().every().at(12, 00)


class TestScheduledJobs(unittest.TestCase):
    def test_job_create_correctly(self):
        def job_func():
            pass
        schedule = Schedule().every().day().at(12, 00)
        job = ScheduledJob(schedule, job_func)

        expected_time = (datetime.now()
                         + timedelta(days=1)).replace(hour=12, minute=0,
                                                      second=0, microsecond=0)

        self.assertEqual(job.func, job_func)
        self.assertEqual(job.next_run, expected_time)
        self.assertFalse(job.should_run())

    def test_job_run_correctly(self):
        test_func = MagicMock()
        schedule = Schedule().every().day().at(12, 00)
        job = ScheduledJob(schedule, test_func)

        job.run()
        test_func.assert_called_once()


class TestScheduler(unittest.TestCase):
    def test_creates_correctly(self):
        scheduler = Scheduler()
        self.assertEqual(len(scheduler.jobs), 0)

    def test_adds_job_correctly(self):
        test_func = MagicMock()
        schedule = Schedule().every().day().at(12, 00)
        job = ScheduledJob(schedule, test_func)

        scheduler = Scheduler()
        scheduler.add_job(job)

        self.assertIn(job, scheduler.jobs)

    def test_runs_jobs_correctly(self):
        test_func = MagicMock()
        schedule = Schedule().every().day().at(12, 00)
        job = ScheduledJob(schedule, test_func)

        job.should_run = MagicMock(return_value=True)

        scheduler = Scheduler()
        scheduler.add_job(job)

        scheduler.run_pending()
        test_func.assert_called_once()

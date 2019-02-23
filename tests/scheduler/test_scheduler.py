from unittest.mock import MagicMock
from phial.scheduler import Scheduler, Schedule, ScheduledJob


def test_creates_correctly() -> None:
    scheduler = Scheduler()
    assert len(scheduler.jobs) == 0


def test_adds_job_correctly() -> None:
    test_func = MagicMock()
    schedule = Schedule().every().day().at(12, 00)
    job = ScheduledJob(schedule, test_func)

    scheduler = Scheduler()
    scheduler.add_job(job)

    assert job in scheduler.jobs


def test_runs_jobs_correctly() -> None:
    test_func = MagicMock()
    schedule = Schedule().every().day().at(12, 00)
    job = ScheduledJob(schedule, test_func)

    job.should_run = MagicMock(return_value=True)  # type: ignore

    scheduler = Scheduler()
    scheduler.add_job(job)

    scheduler.run_pending()
    test_func.assert_called_once()

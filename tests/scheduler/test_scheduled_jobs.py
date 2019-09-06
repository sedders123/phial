"""Test ScheduledJob class."""
from datetime import datetime, timedelta
from unittest.mock import MagicMock

from freezegun import freeze_time  # type: ignore

from phial.scheduler import Schedule, ScheduledJob


@freeze_time('2018-01-01 13:00:00')  # type: ignore
def test_job_create_correctly() -> None:
    """Test ScheduledJob creates correctly."""
    def job_func() -> None:
        pass
    schedule = Schedule().every().day().at(12, 00)
    job = ScheduledJob(schedule, job_func)

    expected_time = (datetime.now() + timedelta(days=1)) \
        .replace(hour=12, minute=0, second=0, microsecond=0)

    assert job.func == job_func
    assert job.next_run == expected_time
    assert not job.should_run()


def test_job_run_correctly() -> None:
    """Test ScheduledJob runs correctly."""
    test_func = MagicMock()
    schedule = Schedule().every().day().at(12, 00)
    job = ScheduledJob(schedule, test_func)

    job.run()
    test_func.assert_called_once_with()  # TODO: Remove 'with' once Python 3.5 support is removed. # noqa: E501


def test_job_reschedules_after_failure() -> None:
    """Tests ScheduledJobs reschedule after failure."""
    def test() -> None:
        raise Exception

    schedule = Schedule().every().day().at(12, 00)
    job = ScheduledJob(schedule, test)

    job.run()
    assert job.next_run is not None

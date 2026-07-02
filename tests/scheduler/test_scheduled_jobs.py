"""Test ScheduledJob class."""

from datetime import UTC, datetime, timedelta
from unittest.mock import MagicMock
from zoneinfo import ZoneInfo

from freezegun import freeze_time

from phial.scheduler import Schedule, ScheduledJob


@freeze_time("2018-01-01 13:00:00")
def test_job_create_correctly() -> None:
    """Test ScheduledJob creates correctly."""
    schedule = Schedule().every().day().at(12, 00)

    def job_func() -> None:
        pass

    job = ScheduledJob(schedule, job_func)

    expected_time = (datetime.now(tz=UTC) + timedelta(days=1)).replace(
        hour=12,
        minute=0,
        second=0,
        microsecond=0,
    )

    assert job.func == job_func
    assert job.next_run == expected_time
    assert not job.should_run()


def test_job_run_correctly() -> None:
    """Test ScheduledJob runs correctly."""
    test_func = MagicMock()
    schedule = Schedule().every().day().at(12, 00)
    job = ScheduledJob(schedule, test_func)

    job.run()
    test_func.assert_called_once()


def test_job_reschedules_after_failure() -> None:
    """Tests ScheduledJobs reschedule after failure."""

    def test() -> None:
        raise Exception

    schedule = Schedule().every().day().at(12, 00)
    job = ScheduledJob(schedule, test)

    job.run()
    assert job.next_run is not None


def test_job_runs_once_on_dst_fall_back_day() -> None:
    """Test a daily zoned job runs once when the local time occurs twice."""
    test_func = MagicMock()
    tz = ZoneInfo("Europe/London")
    schedule = Schedule().every().day().at(1, 00, tz=tz)
    # Clocks go back on 2018-10-28, so 01:00 London happens twice:
    # 01:00 BST (00:00 UTC) and 01:00 GMT (01:00 UTC).
    with freeze_time("2018-10-27 20:00:00") as frozen:
        job = ScheduledJob(schedule, test_func)
        for instant in [
            "2018-10-28 00:00:00",  # first 01:00 BST
            "2018-10-28 00:30:00",
            "2018-10-28 01:00:00",  # second 01:00 GMT
            "2018-10-28 01:30:00",
        ]:
            frozen.move_to(instant)
            if job.should_run():
                job.run()

    test_func.assert_called_once()

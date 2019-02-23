from datetime import datetime, timedelta
from freezegun import freeze_time  # type: ignore
from unittest.mock import MagicMock
from phial.scheduler import Schedule, ScheduledJob


@freeze_time('2018-01-01 13:00:00')  # type: ignore
def test_job_create_correctly() -> None:
    def job_func() -> None:
        pass
    schedule = Schedule().every().day().at(12, 00)
    job = ScheduledJob(schedule, job_func)

    expected_time = (datetime.now()
                     + timedelta(days=1)).replace(hour=12, minute=0,
                                                  second=0, microsecond=0)

    assert job.func == job_func
    assert job.next_run == expected_time
    assert not job.should_run()


def test_job_run_correctly() -> None:
    test_func = MagicMock()
    schedule = Schedule().every().day().at(12, 00)
    job = ScheduledJob(schedule, test_func)

    job.run()
    test_func.assert_called_once()
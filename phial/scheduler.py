from typing import Callable, Optional, List  # noqa: F401
from datetime import timedelta, datetime
from collections import namedtuple

Time = namedtuple("Time", ['hours', 'minutes', 'seconds'])


class Schedule:

    def __init__(self) -> None:
        self._days = 0
        self._at = None  # type: Optional[Time]
        self._hours = 0
        self._minutes = 0
        self._seconds = 0

    def day(self):
        return self.days(1)

    def days(self, value: int):
        self._days = value
        return self

    def at(self, hours: int, minutes: int, seconds: int = 0):
        if self._hours or self._minutes:
            raise Exception("At can only be used on day(s)")
        if not self._days:
            raise Exception("At can only be used on day(s)")
        self._at = Time(hours, minutes, seconds)
        return self

    def hour(self):
        return self.hours(1)

    def hours(self, value: int):
        self._hours = value
        return self

    def minute(self):
        return self.minutes(1)

    def minutes(self, value: int):
        self._minutes = value
        return self

    def second(self):
        return self.seconds(1)

    def seconds(self, value: int):
        self._seconds = value
        return self

    def get_next_run_time(self, last_run: datetime) -> datetime:
        if self._at:
            next_day = last_run + timedelta(days=self._days)
            return next_day.replace(hour=self._at.hours,
                                    minute=self._at.minutes,
                                    second=self._at.seconds,
                                    microsecond=0)

        return last_run + timedelta(days=self._days,
                                    hours=self._hours,
                                    minutes=self._minutes,
                                    seconds=self._seconds)


class Job:
    def __init__(self, schedule: Schedule, func: Callable) -> None:
        self.func = func
        self.schedule = schedule
        self.func = func
        self.next_run = self.schedule.get_next_run_time(datetime.now())

    def should_run(self) -> bool:
        return self.next_run <= datetime.now()

    def run(self) -> None:
        self.func()
        self.next_run = self.schedule.get_next_run_time(datetime.now())


class Scheduler:
    def __init__(self):
        self.jobs = []  # type: List[Job]

    def add_job(self, job: Job) -> None:
        self.jobs.append(job)

    def run_pending(self) -> None:
        jobs_to_run = [job for job in self.jobs
                       if job.should_run()]  # type: List[Job]
        for job in jobs_to_run:
            job.run()

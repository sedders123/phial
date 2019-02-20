from typing import Callable, Optional, List, TypeVar  # noqa: F401
from datetime import timedelta, datetime
from collections import namedtuple

Time = namedtuple("Time", ['hour', 'minute', 'second'])


class Schedule:
    """
    A schedule stores the relative time for something to happen.

    It can be used to compute when the next instance of an event
    should occur.
    """
    def __init__(self) -> None:
        self._days = 0
        self._at = None  # type: Optional[Time]
        self._hours = 0
        self._minutes = 0
        self._seconds = 0

    def every(self) -> 'Schedule':
        """
        Syntatic sugar to allow the declaration of schedules to be more
        like an English sentence.

        ::

            schedule = Schedule().every().day()
        """
        return self

    def day(self) -> 'Schedule':
        """
        Adds a day to the relative time till the next event

        ::

            schedule = Schedule().every().day()
        """
        return self.days(1)

    def days(self, value: int) -> 'Schedule':
        """
        Adds the specified number of days to the relative time till the next
        event.
        ::

            schedule = Schedule().every().days(2)

        :param value: The number of days to wait between events
        """
        self._days = value
        return self

    def at(self, hour: int, minute: int, second: int = 0) -> 'Schedule':
        """
        Specifies the time of day the next occurnce will happen.
        NOTE: 'at' can only be used with :meth:`day`.
        ::

            schedule = Schedule().every().day().at(12,00)

        :param hour: The hour of day the next event should happen,
                     when combined with the minute
        :param minute: The minute of day the next event should happen,
                       when combined with the hour
        :param second: The second of day the next event should
                       happen, when combined with the hour and
                       minute.

                       Defaults to 0
        """
        if self._hours or self._minutes:
            raise Exception("'at' can only be used on day(s)")
        if not self._days:
            raise Exception("'at' can only be used on day(s)")
        if self._at:
            raise Exception("'at' can only be set once")
        self._at = Time(hour, minute, second)
        return self

    def hour(self) -> 'Schedule':
        return self.hours(1)

    def hours(self, value: int) -> 'Schedule':
        self._hours = value
        return self

    def minute(self) -> 'Schedule':
        return self.minutes(1)

    def minutes(self, value: int) -> 'Schedule':
        self._minutes = value
        return self

    def second(self) -> 'Schedule':
        return self.seconds(1)

    def seconds(self, value: int) -> 'Schedule':
        self._seconds = value
        return self

    def get_next_run_time(self, last_run: datetime) -> datetime:
        if self._at:
            next_run = last_run.replace(hour=self._at.hour,
                                        minute=self._at.minute,
                                        second=self._at.second,
                                        microsecond=0)
            if next_run <= datetime.now():
                next_run += timedelta(days=self._days)
            return next_run

        return last_run + timedelta(days=self._days,
                                    hours=self._hours,
                                    minutes=self._minutes,
                                    seconds=self._seconds)


class ScheduledJob:
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
    def __init__(self) -> None:
        self.jobs: List[ScheduledJob] = []

    def add_job(self, job: ScheduledJob) -> None:
        self.jobs.append(job)

    def run_pending(self) -> None:
        jobs_to_run: List[ScheduledJob] = [job for job in self.jobs
                                           if job.should_run()]
        for job in jobs_to_run:
            job.run()

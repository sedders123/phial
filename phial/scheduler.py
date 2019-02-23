"""The classes related to scheduling of regular jobs in phial."""
from collections import namedtuple
from datetime import datetime, timedelta
from typing import Callable, List, Optional


class _Time(namedtuple("Time", ['hour', 'minute', 'second'])):
    """Represents a time of day.

    .. py:attribute:: hour

        The hour of day.

    .. py:attribute:: minute

        The minute of the hour.

    .. py:attribute:: second

        The second of the minute.

    """


class Schedule:
    """
    A schedule stores the relative time for something to happen.

    It can be used to compute when the next instance of an event
    should occur.
    """

    def __init__(self) -> None:
        self._days = 0
        self._at: Optional[_Time] = None
        self._hours = 0
        self._minutes = 0
        self._seconds = 0

    def every(self) -> 'Schedule':
        """
        Syntantic sugar to make schedule declaration more readable.

        Syntatic sugar to allow the declaration of schedules to be more
        like an English sentence.

        ::

            schedule = Schedule().every().day()
        """
        return self

    def day(self) -> 'Schedule':
        """
        Adds a day to the relative time till the next event.

        ::

            schedule = Schedule().every().day()
        """
        return self.days(1)

    def days(self, value: int) -> 'Schedule':
        """
        Set the days till the next instance of the event.

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
        self._at = _Time(hour, minute, second)
        return self

    def hour(self) -> 'Schedule':
        """
        Adds an hour to the relative time till the next event.

        ::

            schedule = Schedule().every().hour()
        """
        return self.hours(1)

    def hours(self, value: int) -> 'Schedule':
        """
        Sets the hours till the next instance of the event.

        Adds the specified number of hours to the relative time till the next
        event.

        ::

            schedule = Schedule().every().hours(2)

        :param value: The number of hours to wait between events
        """
        self._hours = value
        return self

    def minute(self) -> 'Schedule':
        """
        Adds a minute to the relative time till the next event.

        ::

            schedule = Schedule().every().minute()
        """
        return self.minutes(1)

    def minutes(self, value: int) -> 'Schedule':
        """
        Sets the minutes till the next instance of the event.

        Adds the specified number of minutes to the relative time till the next
        event.

        ::

            schedule = Schedule().every().minutes(2)

        :param value: The number of minutes to wait between events
        """
        self._minutes = value
        return self

    def second(self) -> 'Schedule':
        """
        Adds a second to the relative time till the next event.

        ::

            schedule = Schedule().every().second()
        """
        return self.seconds(1)

    def seconds(self, value: int) -> 'Schedule':
        """
        Sets the seconds till the next instance of the event.

        Adds the specified number of seconds to the relative time till the next
        event.
        ::

            schedule = Schedule().every().seconds(2)

        :param value: The number of seconds to wait between events
        """
        self._seconds = value
        return self

    def get_next_run_time(self, last_run: datetime) -> datetime:
        """
        Get the next time the job should run.

        Calculates the next time to run, based on the last time the
        event was run.

        :param last_run: The last time the event happened

        :returns: A :obj:`datetime` of when the event should next happen
        """
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
    """A function with a schedule."""

    def __init__(self, schedule: Schedule, func: Callable) -> None:
        self.func = func
        self.schedule = schedule
        self.func = func
        self.next_run = self.schedule.get_next_run_time(datetime.now())

    def should_run(self) -> bool:
        """
        Checks whether the function needs to be run based on the schedule.

        :returns: A :obj:`bool` of whether or not to run
        """
        return self.next_run <= datetime.now()

    def run(self) -> None:
        """Runs the function and calculates + stores the next run time."""
        self.func()
        self.next_run = self.schedule.get_next_run_time(datetime.now())


class Scheduler:
    """A store for Scheduled Jobs."""

    def __init__(self) -> None:
        self.jobs: List[ScheduledJob] = []

    def add_job(self, job: ScheduledJob) -> None:
        """
        Adds a scheuled job to the scheduler.

        :param job: The job to be added to the scheduler
        """
        self.jobs.append(job)

    def run_pending(self) -> None:
        """
        Runs any pending scheduled jobs.

        Runs any ScheduledJobs in the store, where :code:`job.should_run()`
        returns true
        """
        jobs_to_run: List[ScheduledJob] = [job for job in self.jobs
                                           if job.should_run()]
        for job in jobs_to_run:
            job.run()

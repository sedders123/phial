from typing import Callable, Optional, List, TypeVar  # noqa: F401
from datetime import timedelta, datetime
from collections import namedtuple

Time = namedtuple("Time", ['hour', 'minute', 'second'])


class Schedule:
    '''
    A schedule stores the relative time for something to happen.

    It can be used to compute when the next event of an event
    should occur.
    '''
    def __init__(self) -> None:
        self._days = 0
        self._at = None  # type: Optional[Time]
        self._hours = 0
        self._minutes = 0
        self._seconds = 0

    def every(self):
        # type: () -> Schedule
        '''
        Syntatic sugar to allow the declaration of schedules to be more
        like English.
        ::

            schedule = Schedule().every().day()
        '''
        return self

    def day(self):
        # type: () -> Schedule
        '''
        Adds a day to the relative time till the next event
        ::

            schedule = Schedule().every().day()
        '''
        return self.days(1)

    def days(self, value):
        # type: (int) -> Schedule
        '''
        Adds the specified number of days to the relative time till the next
        event.
        ::

            schedule = Schedule().every().days(2)

        Args:
            value(int): The number of days to wait between events
        '''
        self._days = value
        return self

    def at(self, hour, minute, second=0):
        # type: (int, int, int) -> Schedule
        '''
        Specifies the time of day the next occurnce will happen.
        NOTE: 'at' can only be used with :meth:`day`.
        ::

            schedule = Schedule().every().day().at(12,00)

        Args:
            hour(int): The hour of day the next event should happen,
                       when combined with the minute
            minute(int): The minute of day the next event should happen,
                         when combined with the hour
            second(int, optional): The second of day the next event should
                                   happen, when combined with the hour and
                                   minute.
                                   Defaults to 0
        '''
        if self._hours or self._minutes:
            raise Exception("'at' can only be used on day(s)")
        if not self._days:
            raise Exception("'at' can only be used on day(s)")
        if self._at:
            raise Exception("'at' can only be set once")
        self._at = Time(hour, minute, second)
        return self

    def hour(self):
        # type: () -> Schedule
        '''
        Adds an hour to the relative time till the next event.
        ::

            schedule = Schedule().every().hour()
        '''
        return self.hours(1)

    def hours(self, value):
        # type: (int) -> Schedule
        '''
        Adds the specified number of hours to the relative time till the next
        event.
        ::

            schedule = Schedule().every().hours(2)

        Args:
            value(int): The number of hours to wait between events
        '''
        self._hours = value
        return self

    def minute(self):
        # type: () -> Schedule
        '''
        Adds a minute to the relative time till the next event
        ::

            schedule = Schedule().every().minute()
        '''
        return self.minutes(1)

    def minutes(self, value):
        # type: (int) -> Schedule
        '''
        Adds the specified number of minutes to the relative time till the next
        event.
        ::

            schedule = Schedule().every().minutes(2)

        Args:
            value(int): The number of minutes to wait between events
        '''
        self._minutes = value
        return self

    def second(self):
        # type: () -> Schedule
        '''
        Adds a second to the relative time till the next event
        ::

            schedule = Schedule().every().second()
        '''
        return self.seconds(1)

    def seconds(self, value):
        # type: (int) -> Schedule
        '''
        Adds the specified number of seconds to the relative time till the next
        event.
        ::

            schedule = Schedule().every().seconds(2)

        Args:
            value(int): The number of seconds to wait between events
        '''
        self._seconds = value
        return self

    def get_next_run_time(self, last_run: datetime) -> datetime:
        '''
        Calculates the next time to run, based on the last time the
        event was run.

        Args:
            last_run(datetime): The last time the event happened

        Returns:
            A :obj:`datetime` of when the event should next happen
        '''
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
    '''
    A function with a schedule
    '''
    def __init__(self, schedule: Schedule, func: Callable) -> None:
        self.func = func
        self.schedule = schedule
        self.func = func
        self.next_run = self.schedule.get_next_run_time(datetime.now())

    def should_run(self) -> bool:
        '''
        Checks whether the function needs to be run based on the schedule.

        Returns:
            A :obj:`bool` of whether or not to run
        '''
        return self.next_run <= datetime.now()

    def run(self) -> None:
        '''
        Runs the function and calculates + stores the next run time
        '''
        self.func()
        self.next_run = self.schedule.get_next_run_time(datetime.now())


class Scheduler:
    '''
    A store for Scheduled Jobs
    '''
    def __init__(self) -> None:
        self.jobs = []  # type: List[ScheduledJob]

    def add_job(self, job: ScheduledJob) -> None:
        '''
        Adds a scheuled job to the scheduler

        Args:
            job(ScheduledJob): The job to be added to the scheduler
        '''
        self.jobs.append(job)

    def run_pending(self) -> None:
        '''
        Runs any ScheduledJobs in the store, where job.should_run() returns
        true
        '''
        jobs_to_run = [job for job in self.jobs
                       if job.should_run()]  # type: List[ScheduledJob]
        for job in jobs_to_run:
            job.run()

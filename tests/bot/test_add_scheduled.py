"""Test Add Scheduled."""
from phial import Message, Phial, Schedule


def test_add_scheduled_command() -> None:
    """Test add_scheduled works correctly."""
    def test(message: Message) -> None:
        pass

    bot = Phial('token', {})
    bot.add_scheduled(Schedule().seconds(30), test)

    assert len(bot.scheduler.jobs) == 1
    assert bot.scheduler.jobs[0].func is test


def test_add_scheduled_decorator() -> None:
    """Test scheduled decorator works correctly."""
    bot = Phial('token', {})

    @bot.scheduled(Schedule().seconds(30))
    def test(message: Message) -> None:
        pass

    assert len(bot.scheduler.jobs) == 1
    assert bot.scheduler.jobs[0].func is test

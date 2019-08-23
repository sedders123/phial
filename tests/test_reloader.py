"""Test reloader."""
import pytest

from phial._reloader import (
    ReloaderLoop,
    WatchdogReloaderLoop,
    _find_observable_paths,
    _get_args_for_reloading,
    _iter_module_files,
    iteritems,
)


def test_find_observable_paths() -> None:
    """Test find_observable_paths."""
    paths = _find_observable_paths()
    assert len(paths) != 0


def test_find_observable_paths_with_extra_file() -> None:
    """Test find_observable_paths with extra files."""
    paths = _find_observable_paths("extra file")
    assert len(paths) != 0


def test_iteritems() -> None:
    """Test iteritems."""
    d = {"a": 1}
    for item in iteritems(d):
        assert item[0] == "a"
        assert item[1] == 1


def test_iter_module_files() -> None:
    """Test _iter_module_files."""
    for i in _iter_module_files():
        assert len(i) != 0


def test_watchdog_reloader_loop() -> None:
    """Test Watchdog Reloader Loop."""
    loop = WatchdogReloaderLoop()
    assert loop is not None


def test_watchdog_reloader_loop_log_reload() -> None:
    """Test Watchdog Reloader Loop log reload."""
    loop = WatchdogReloaderLoop()
    loop.log_reload("filename")


def test_watchdog_reloader_loop_trigger_reload() -> None:
    """Test Watchdog Reloader Loop trigger reload."""
    loop = WatchdogReloaderLoop()
    loop.trigger_reload("filename")


def test_reloader_loop_run() -> None:
    """Test Reloader Loop run."""
    loop = ReloaderLoop()
    loop.run()


def test_reloader_loop_log_reload() -> None:
    """Test Reloader Loop trigger reload."""
    loop = ReloaderLoop()
    with pytest.raises(SystemExit) as e:
        loop.trigger_reload("filename")
    assert e is not None


def test_reloader_get_args_for_reloading() -> None:
    """Test reloader _get_args_for_reloading."""
    args = _get_args_for_reloading()
    assert args is not None

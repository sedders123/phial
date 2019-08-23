"""Hot Reload Logic."""
# This code was copied from the werkzeug project
# Project: https://palletsprojects.com/p/werkzeug/
#
# Original License
# Copyright 2007 Pallets
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# Redistributions of source code must retain the above copyright notice, this
# list of conditions and the following disclaimer.
#
# Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
#
# Neither the name of the copyright holder nor the names of its contributors
# may be used to endorse or promote products derived from this software
# without specific prior written permission.
#
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF
# THE POSSIBILITY OF SUCH DAMAGE.
import os
import subprocess
import sys
import threading
from itertools import chain
from typing import (
    Any,
    Callable,
    Dict,
    Generator,
    Iterable,
    List,
    Optional,
    Set,
    Tuple,
)


def iteritems(d: Any, *args: Any, **kwargs: Any) -> Any:
    """Iterate items."""
    return iter(d.items(*args, **kwargs))


def _iter_module_files() -> Generator[str, None, None]:
    """
    This iterates over all relevant Python files.

    It goes through all loaded files from modules, all files in folders of
    already loaded modules as well as all files reachable through a package.
    """
    for module in list(sys.modules.values()):
        if module is None:
            continue
        filename = getattr(module, "__file__", None)
        if filename:
            if os.path.isdir(filename) and os.path.exists(
                os.path.join(filename, "__init__.py"),
            ):
                filename = os.path.join(filename, "__init__.py")

            old = None
            while not os.path.isfile(filename):
                old = filename
                filename = os.path.dirname(filename)
                if filename == old:
                    break
            else:
                if filename[-4:] in (".pyc", ".pyo"):
                    filename = filename[:-1]
                yield filename


def _find_observable_paths(extra_files:
                           Optional[Iterable[str]] = None) -> Set[str]:
    """Finds all paths that should be observed."""
    rv = {os.path.dirname(os.path.abspath(x)) if os.path.isfile(x) else
          os.path.abspath(x) for x in sys.path}

    for filename in extra_files or ():
        rv.add(os.path.dirname(os.path.abspath(filename)))

    for module in list(sys.modules.values()):
        fn = getattr(module, "__file__", None)
        if fn is None:
            continue
        fn = os.path.abspath(fn)
        rv.add(os.path.dirname(fn))

    return _find_common_roots(rv)


def _get_args_for_reloading() -> List[str]:  # pragma: no cover
    """
    Returns the executable.

    This contains a workaround for windows if the executable is
    incorrectly reported to not have the .exe extension which can
    cause bugs on reloading.  This also contains a workaround for
    linux where the file is executable (possibly with a program
    other than python)
    """
    rv = [sys.executable]
    py_script = os.path.abspath(sys.argv[0])
    args = sys.argv[1:]
    # Need to look at main module to determine how it was executed.
    __main__ = sys.modules["__main__"]

    if __main__.__package__ is None:
        # Executed a file, like "python app.py".
        if os.name == "nt":
            # Windows entry points have ".exe" extension and should be
            # called directly.
            if not os.path.exists(py_script) and os.path.exists(py_script
                                                                + ".exe"):
                py_script += ".exe"

            if (
                os.path.splitext(rv[0])[1] == ".exe"
                and os.path.splitext(py_script)[1] == ".exe"
            ):
                rv.pop(0)

        elif os.path.isfile(py_script) and os.access(py_script, os.X_OK):
            # The file is marked as executable. Nix adds a wrapper that
            # shouldn't be called with the Python executable.
            rv.pop(0)

        rv.append(py_script)
    else:
        # Executed a module, like "python -m werkzeug.serving".
        py_module = __main__.__package__
        name = os.path.splitext(os.path.basename(py_script))[0]

        if name != "__main__":
            py_module += "." + name

        rv.extend(("-m", py_module.lstrip(".")))

    rv.extend(args)
    return rv


def _find_common_roots(paths: Any) -> Set[str]:
    """Out of some paths it finds the common roots that need monitoring."""
    paths = [x.split(os.path.sep) for x in paths]
    root: Dict[str, Dict] = {}
    for chunks in sorted(paths, key=len, reverse=True):
        node = root
        for chunk in chunks:
            node = node.setdefault(chunk, {})
        node.clear()

    rv = set()

    def _walk(node: Dict[str, Dict], path: Tuple[Any, ...]) -> None:
        for prefix, child in iteritems(node):
            _walk(child, path + (prefix,))
        if not node:
            rv.add("/".join(path))

    _walk(root, ())
    return rv


class ReloaderLoop(object):
    """Reloader loop."""

    name: Optional[str] = None

    def __init__(self, extra_files: Optional[List[str]] = None,
                 interval: int = 1):
        self.extra_files = {os.path.abspath(x) for x in extra_files or ()}
        self.interval = interval

    def run(self) -> None:
        """Run."""
        pass

    def restart_with_reloader(self) -> int:  # pragma: no cover
        """
        Restart the reloader.

        Spawn a new Python interpreter with the same arguments as this one,
        but running the reloader thread.
        """
        while 1:
            # _log("info", " * Restarting with %s" % self.name)
            args = _get_args_for_reloading()
            new_environ = os.environ.copy()

            new_environ["WERKZEUG_RUN_MAIN"] = "true"
            exit_code = subprocess.call(args, env=new_environ, close_fds=False)
            if exit_code != 3:
                return exit_code

    def trigger_reload(self, filename: str) -> None:
        """Trigger Reload."""
        self.log_reload(filename)
        sys.exit(3)

    def log_reload(self, filename: str) -> None:
        """Log a reload has occured."""
        filename = os.path.abspath(filename)
        # _log("info", " * Detected change in %r, reloading" % filename)


class StatReloaderLoop(ReloaderLoop):
    """Stat reloader loop."""

    name = "stat"

    def run(self) -> None:  # pragma: no cover
        """Run."""
        mtimes: Dict[str, float] = {}
        while 1:
            for filename in chain(_iter_module_files(), self.extra_files):
                try:
                    mtime = os.stat(filename).st_mtime
                except OSError:
                    continue

                old_time = mtimes.get(filename)
                if old_time is None:
                    mtimes[filename] = mtime
                    continue
                elif mtime > old_time:
                    self.trigger_reload(filename)
            # self._sleep(self.interval)


class WatchdogReloaderLoop(ReloaderLoop):
    """Watchdog Reloader Loop."""

    def __init__(self, *args: Any, **kwargs: Any):
        ReloaderLoop.__init__(self, *args, **kwargs)
        from watchdog.observers import Observer  # type: ignore
        from watchdog.events import FileSystemEventHandler  # type: ignore

        self.observable_paths: Set[str] = set()

        def _check_modification(filename: str) -> None:
            if filename in self.extra_files:
                self.trigger_reload(filename)
            dirname = os.path.dirname(filename)
            if dirname.startswith(tuple(self.observable_paths)):
                if filename.endswith((".pyc", ".pyo", ".py")):
                    self.trigger_reload(filename)

        class _CustomHandler(FileSystemEventHandler):  # type: ignore
            def on_created(self, event):  # type: ignore
                _check_modification(event.src_path)

            def on_modified(self, event):  # type: ignore
                _check_modification(event.src_path)

            def on_moved(self, event):  # type: ignore
                _check_modification(event.src_path)
                _check_modification(event.dest_path)

            def on_deleted(self, event):  # type: ignore
                _check_modification(event.src_path)

        reloader_name = Observer.__name__.lower()
        if reloader_name.endswith("observer"):
            reloader_name = reloader_name[:-8]
        reloader_name += " reloader"

        self.name = reloader_name

        self.observer_class = Observer
        self.event_handler = _CustomHandler()
        self.should_reload = False

    def trigger_reload(self, filename: str) -> None:
        """Trigger a reload."""
        # This is called inside an event handler, which means throwing
        # SystemExit has no effect.
        # https://github.com/gorakhargosh/watchdog/issues/294
        self.should_reload = True
        self.log_reload(filename)

    def run(self) -> None:  # pragma: no cover
        """Run."""
        watches: Dict[str, Any] = {}
        observer = self.observer_class()
        observer.start()

        try:
            while not self.should_reload:
                to_delete = set(watches)
                paths = _find_observable_paths(self.extra_files)
                for path in paths:
                    if path not in watches:
                        try:
                            watches[path] = observer.schedule(
                                self.event_handler, path, recursive=True,
                            )
                        except OSError:
                            # Clear this path from list of watches We don't
                            # want the same error message showing again in
                            # the next iteration.
                            watches[path] = None
                    to_delete.discard(path)
                for path in to_delete:
                    watch = watches.pop(path, None)
                    if watch is not None:
                        observer.unschedule(watch)
                self.observable_paths = paths
                # self._sleep(self.interval)
        finally:
            observer.stop()
            observer.join()

        sys.exit(3)


reloader_loops = {"stat": StatReloaderLoop, "watchdog": WatchdogReloaderLoop}

try:
    __import__("watchdog.observers")
except ImportError:
    reloader_loops["auto"] = reloader_loops["stat"]
else:
    reloader_loops["auto"] = reloader_loops["watchdog"]


def ensure_echo_on() -> None:  # pragma: no cover
    """
    Ensure that echo mode is enabled.

    Some tools such as PDB disable it which causes usability issues after
    reload.
    """
    # tcgetattr will fail if stdin isn't a tty
    if not sys.stdin.isatty():
        return
    try:
        import termios
    except ImportError:
        return
    attributes = termios.tcgetattr(sys.stdin)
    if not attributes[3] & termios.ECHO:  # type: ignore
        attributes[3] |= termios.ECHO  # type: ignore
        termios.tcsetattr(sys.stdin, termios.TCSANOW, attributes)


def run_with_reloader(
    main_func: Callable,
    extra_files: Optional[List[str]] = None,
    interval: int = 1,
    reloader_type: str = "auto",
) -> None:  # pragma: no cover
    """Run the given function in an independent python interpreter."""
    import signal

    reloader = reloader_loops[reloader_type](extra_files, interval)
    signal.signal(signal.SIGTERM, lambda *args: sys.exit(0))
    try:
        if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
            ensure_echo_on()
            t = threading.Thread(target=main_func, args=())
            t.setDaemon(True)
            t.start()
            reloader.run()
        else:
            sys.exit(reloader.restart_with_reloader())
    except KeyboardInterrupt:
        pass

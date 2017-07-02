from contextlib import contextmanager
from io import StringIO
import sys


@contextmanager
def captured_output():
    new_out, new_err = StringIO(), StringIO()
    old_out, old_err = sys.stdout, sys.stderr
    try:
        sys.stdout, sys.stderr = new_out, new_err
        yield sys.stdout, sys.stderr
    finally:
        sys.stdout, sys.stderr = old_out, old_err


class MockTrueFunc():
    def true_once(self):
        yield True
        yield False

    def __init__(self):
        self.gen = self.true_once()

    def __call__(self):
        return next(self.gen)

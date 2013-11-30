"""
Chronic is a module designed to do simple profiling of your python code while
giving you full control of the granularity of measurement.  It maintains the
hierarchy of the call tree, but only at the levels you care about.  The timing
results can easily be captured as JSON and logged for analysis in postgres or
mongodb.

You may use the @time decorator or the Timer context manager:

>>> @time
>>> def func():
>>>     with Timer('bar'):
>>>         pass
>>> func()
>>> timings
{
    'func': {
        'total_elapsed': 38.5,
        'count': 1,
        'average_elapsed': 38.5
        'timings': {
            'bar': {
                'total_elapsed': 20.52,
                'count': 1
                'average_elapsed': 20.52
            }
        }
    }
}

"""

import sys
import time as systime
import threading
from functools import partial, wraps

from signals import Signal
from proxy import Proxy


_local = threading.local()
if sys.platform == "win32":
    # On Windows, the best timer is time.clock()
    _clock = systime.clock
else:
    # On most other platforms the best timer is time.time()
    _clock = systime.time
post_timing = Signal(name='post timing')


class Timer(object):
    '''A context manager for timing blocks of code.

    Use chronic.timings to obtain the results.

    Arguments:
    name -- A unique name for the timing.
    clock -- A function that returns the current time.  Mostly for testing,
             default is the system clock.
    '''
    def __init__(self, name, clock=None):
        self.name = name
        self._clock = clock if clock is not None else _clock

    def _push(self):
        if not hasattr(_local, 'stopwatch'):
            _local.stopwatch = {'current': {}, 'stack': []}
        current = _local.stopwatch['current']
        _local.stopwatch['stack'].append((self.name, current))
        current['timings'] = current.get('timings', {})
        current['timings'][self.name] = current['timings'].get(self.name, {})
        new = current['timings'][self.name]
        _local.stopwatch['current'] = new

    def _pop(self):
        _, last = _local.stopwatch['stack'].pop()
        _local.stopwatch['current'] = last

    def __enter__(self):
        self._push()
        self.start = self._clock()

    def __exit__(self, type, val, tb):
        elapsed = self._clock() - self.start
        current = _local.stopwatch['current']
        current['total_elapsed'] = elapsed + current.get('total', 0)
        current['count'] = 1 + current.get('count', 0)
        current['average_elapsed'] = (current['total_elapsed'] /
                                      current['count'])
        current_stack = stack
        self._pop()
        post_timing.emit(elapsed, current, current_stack)


def time(func=None, name=None, clock=None):
    '''A decorator for timing function calls.

    Use chronic.timings to obtain the results.

    Arguments:
    name -- A unique name for the timing.  Defaults to the function name.
    clock -- A function that returns the current time.  Mostly for testing,
             default is the system clock.
    '''

    # When this decorator is used with optional parameters:
    #
    #   @time(name='timed_thing')
    #   def func():
    #       pass
    #
    # The result of this decorator should be a function which will receive
    # the function to wrap as an argument, and return the wrapped function.
    if func is None:
        return partial(time, name=name, clock=clock)

    @wraps(func)
    def _inner(*args, **kws):
        with Timer(name or func.__name__, clock=clock):
            result = func(*args, **kws)
        return result
    return _inner


def _get_timings():
    if hasattr(_local, 'stopwatch'):
        return _local.stopwatch['current'].get('timings', {})


def _get_stack():
    if hasattr(_local, 'stopwatch'):
        return tuple(name for name, _ in _local.stopwatch['stack'])


timings = Proxy(_get_timings, doc='''This variable always holds all completed
timing information for the current scope.  Information is available as a dict
with a key for each timing (the name of the timer).  The value of each timing
is a dict with three keys:
    * total_elapsed: the elapsed execution time of the code (including all
      subtimings) for all runs of this block.  The unit is seconds by default.
      If you pass in your own clock function, the unit is whatever the unit of
      the clock.
    * count: the number of times the timed block was run.
    * average_elapsed: the average elapsed time for each run of this block.
    * timings: a dict of all subtimings that were completed while inside this
      block
''')
stack = Proxy(_get_stack)


def clear():
    _local.stopwatch = {'current': {}, 'stack': []}

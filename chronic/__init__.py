import sys
import time as systime
import threading
from signals import Signal


_local = threading.local()
if sys.platform == "win32":
    # On Windows, the best timer is time.clock()
    _timer = systime.clock
else:
    # On most other platforms the best timer is time.time()
    _timer = systime.time
post_timing = Signal(name='post timing')


class Timer(object):
    def push(self):
        if not hasattr(_local, 'stopwatch'):
            _local.stopwatch = {'current': {}, 'stack': []}
        current = _local.stopwatch['current']
        _local.stopwatch['stack'].append((self.name, current))
        current['timings'] = current.get('timings', {})
        current['timings'][self.name] = current['timings'].get(self.name, {})
        new = current['timings'][self.name]
        _local.stopwatch['current'] = new

    def pop(self):
        _, last = _local.stopwatch['stack'].pop()
        _local.stopwatch['current'] = last

    def __init__(self, name):
        self.name = name

    def __enter__(self):
        self.push()
        self.start = _timer()

    def __exit__(self, type, val, tb):
        elapsed = _timer() - self.start
        current = _local.stopwatch['current']
        current['total_elapsed'] = elapsed + current.get('total', 0)
        current['count'] = 1 + current.get('count', 0)
        current['average_elapsed'] = (current['total_elapsed'] /
                                      current['count'])
        self.pop()
        post_timing.emit(current, stack)


def time(f, name=None):
    def _inner(*args, **kws):
        with Timer(name or f.__name__):
            result = f(*args, **kws)
        return result
    return _inner


def timings():
    return _local.stopwatch['current'].get('timings', {})


def stack():
    return [name for name, _ in _local.stopwatch['stack']]

#  @timed
#  def func(a, b):
#      inner(a)
#      inner(b)
#      with stopwatch('bar'):
#          inner(c)
#          inner(d)
#
#  timings = {
#      'func': {
#          'total': 38.5,
#          'timings': {
#              'inner': {
#                  'total':  20.12,
#                  'avg': 10.06,
#                  'count': 2
#              },
#              'bar': {
#                  'total': 20.52,
#                  'timings': {
#                      'inner': {
#                          'total': 20.12
#                      }
#                  }
#              }
#          }
#      }
#  }

import os
import sys
sys.path.append(os.path.dirname(__file__) + '/..')

from chronic import time, Timer, timings, stack, post_timing
import time as systime


def test_stack():
    with Timer('a'):
        with Timer('b'):
            assert stack() == ['a', 'b']


def test_timings():
    with Timer('a'):
        systime.sleep(0.1)

    assert 'a' in timings(), "Timings dict did not contain timing name"
    a = timings()['a']
    assert 'total_elapsed' in a, "Timing didn't include a total_elapsed"
    assert abs(a['total_elapsed'] - 0.1) < 0.01


def test_time_decorator():
    @time
    def timed_func():
        systime.sleep(0.1)

    timed_func()

    assert 'timed_func' in timings()
    a = timings()['timed_func']
    assert 'total_elapsed' in a, "Timing didn't include a total_elapsed"
    assert abs(a['total_elapsed'] - 0.1) < 0.01


def test_signals():
    d = {}

    def callback(*args, **kws):
        d['called'] = 1

    post_timing.connect(callback)
    with Timer('a'):
        pass

    assert d['called'] is 1


if __name__ == '__main__':
    module = sys.modules[__name__]
    tests = [f for f in dir(module) if 'test_' in f]
    for test in tests:
        getattr(module, test)()

import os
import sys
import threading
import unittest
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from chronic import clear, time, Timer, timings, stack, post_timing


class MockClock(object):
    def __init__(self):
        self.time = 1000

    def add_seconds(self, seconds):
        self.time += seconds

    def get_time(self):
        return self.time


class BasicTest(unittest.TestCase):
    def setUp(self):
        clear()

    def test_stack(self):
        with Timer('a'):
            with Timer('b'):
                assert stack == ('a', 'b')

    def test_timings(self):
        clock = MockClock()
        with Timer('a', clock=clock.get_time):
            clock.add_seconds(10)

        with Timer('a', clock=clock.get_time):
            clock.add_seconds(5)

        self.assertIn('a', timings,
                      "Timings dict did not contain timing name")
        a = timings['a']
        self.assertIn('total_elapsed', a,
                      "Timing didn't include a total_elapsed")
        self.assertEquals(a['total_elapsed'], 15)

        self.assertIn('a', timings(),
                      "Timings dict could not be accessed as a function.")

    def test_time_decorator(self):
        clock = MockClock()

        @time(clock=clock.get_time)
        def timed_func():
            clock.add_seconds(10)

        timed_func()

        self.assertIn('timed_func', timings)
        a = timings['timed_func']
        self.assertIn('total_elapsed', a,
                      "Timing didn't include a total_elapsed")
        self.assertEquals(a['total_elapsed'], 10)

    def test_time_decorator_no_args(self):

        @time
        def timed_func():
            pass

        timed_func()
        self.assertIn('timed_func', timings)
        a = timings['timed_func']
        self.assertIn('total_elapsed', a,
                      "Timing didn't include a total_elapsed")

    def test_timings_are_emptied_between_tests(self):
        '''
        If not, a lot of the asserts in these tests may incorrectly pass.
        '''
        self.assertEquals({}, timings)

    def test_signals(self):
        d = {}

        def callback(*args, **kws):
            d['called'] = 1

        post_timing.connect(callback)
        with Timer('a'):
            pass

        assert d['called'] is 1


class ThreadingTest(unittest.TestCase):
    def test_timings_do_not_bleed(self):
        all_timings = []

        def time_stuff():
            clock = MockClock()
            for i in range(5):
                with Timer('test', clock=clock.get_time):
                    clock.add_seconds(1)
            all_timings.append(timings.copy())

        threads = []
        for i in range(4):
            t = threading.Thread(target=time_stuff)
            t.start()
            threads.append(t)

        for t in threads:
            t.join()

        for ts in all_timings:
            self.assertIn('test', ts)
            self.assertEquals(ts['test']['count'], 5)

Chronic - Python Mini-Profiler
==============================

Chronic is halfway between a simple timer and a profiler.  It does not track every call like a profiler does.  You must specify what levels you want to time.  But it keeps the hierarchy of your timings intact.

## Usage

To time a block of code, you can use either the `@time` decorator or the `Timer` context manager.

```python
import chronic

@chronic.time
def long_running_method():
  # Do something here

with chronic.Timer('crunch_numbers'):
  # Crunch numbers here
```

At any point, you can get the information about completed timing info from `chronic.timings`.  This is a proxy to state held in a thread local about all timed blocks captured so far.

```python
>>> import chronic
>>> chronic.timings
{
  'long_running_method': {
    'total_elapsed': 3.068,
    'average_elapsed': 3.068,
    'count': 1
  },
  'crunch_numbers': {
    'total_elapsed': 1.884,
    'average_elapsed': 1.884,
    'count': 1
  }
}
```

`chronic.timings` is a dict with keys for each timed block of code.  If you use the context manager, you must specify a name.  When using the decorator, you may optionally specify the name, or chronic will use theh function name as a default.

Each timing is itself a dict with the following keys:

* total_elapsed: the elapsed execution time of the code (including all
  subtimings) for all runs of this block.  The unit is seconds by default.
  If you pass in your own clock function, the unit is whatever the unit of
  the clock.
* count: the number of times the timed block was run.
* average_elapsed: the average elapsed time for each run of this block.
* timings: a dict of all subtimings that were completed while inside this
  block.


`chronic.stack` is a tuple of the names of all timed blocks in the call stack above the current context.

```
>>> import chronic
>>> @chronic.time
>>> def time_two():
>>>     with chronic.Timer('block2'):
>>>         print chronic.stack
>>> time_two()
('time_two', 'block2')
```

Finally, you can install signal handlers to be called on the completion of all timings.
Here's how you might send all timing data to (statsd)[https://github.com/etsy/statsd/]:

```python
>>> import chronic
>>> from statsd import StatsClient
>>> statsd = StatsClient()
>>> def send_to_statsd(elapsed, timings, stack):
>>>     statsd.timing('.'.join(stack), elapsed * 1000)
>>> chronic.post_timing.connect(send_to_statsd)
```

## Examples

```python
import chronic
from pprint import pprint


@chronic.time
def time_one():
    pass


@chronic.time
def time_two():
    with chronic.Timer('block2'):
        print chronic.stack
        # ('time_two', 'block2')
    pprint(chronic.timings)
    # prints local view of timings
    # {'block2': {'average_elapsed': 1.0967254638671875e-05,
    #             'count': 1,
    #             'total_elapsed': 1.0967254638671875e-05}}

with chronic.Timer('block1'):
    time_one()

pprint(chronic.timings)


def print_done(elapsed, timings, stack):
    print stack
    pprint(timings)

time_one()
chronic.post_timing.connect(print_done)
time_one()
# []
# 9.5367431640625e-07
# {'average_elapsed': 9.5367431640625e-07,
#  'count': 2,
#  'total_elapsed': 1.9073486328125e-06} 
chronic.post_timing.disconnect(print_done)


time_two()
# ['time_two', 'block2']
# {'block2': {'average_elapsed': 5.9604644775390625e-06,
#             'count': 1,
#             'total_elapsed': 5.9604644775390625e-06}}
```


This software is licensed under the MIT license. See the details in the file called LICENSE.

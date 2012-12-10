Chronic - Python Profiler
=========================

Chronic is halfway between a simple timer and a profiler.  It does not track every call like a profiler does.  You must specify what levels you want to time.  But it keeps the hierarchy of your timings intact.

```python
import chronic
from pprint import pprint


@chronic.time
def time_one():
    pass


@chronic.time
def time_two():
    with chronic.Timer('block2'):
        print chronic.stack()
        # ['time_two', 'block2']
    pprint(chronic.timings())
    # prints local view of timings
    # {'block2': {'average_elapsed': 1.0967254638671875e-05,
    #             'count': 1,
    #             'total_elapsed': 1.0967254638671875e-05}}

with chronic.Timer('block1'):
    time_one()

pprint(chronic.timings())


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

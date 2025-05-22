# Porting Python Packages to Support Free-Threading

This document discusses porting an existing Python package to support free-threading Python.

## Current status (as of early 2025)

Many Python packages, particularly packages relying on C
extension modules, do not consider multithreaded use or make strong
assumptions about the GIL providing sequential consistency in multithreaded
contexts. These packages will:

- fail to produce deterministic results on the free-threaded build
- may, if there are C extensions involved, crash the interpreter in multithreaded use in ways that are impossible on the
    GIL-enabled build

Attempting to parallelize many workflows using the Python
[threading](https://docs.python.org/3/library/threading.html) module will not
produce any speedups on the GIL-enabled build, so thread safety issues that are possible even with the
GIL are not hit often since users do not make use of threading as much as other
parallelization strategies. This means many codebases have threading bugs that
up-until-now have only been theoretical or present in niche use cases. With
free-threading, many more users will want to use Python threads.

This means we must analyze Python codebases to identify supported and
unsupported multithreaded workflows and make changes to fix thread safety
issues. Extra care must be taken to address this need, particularly when using low-level C, C++, Cython, and Rust
code exposed to Python. Even pure Python codebases can exhibit
non-determinism and races in the free-threaded build that are either very
unlikely or impossible in the default configuration of the GIL-enabled build.

For a more in-depth look at the differences between the GIL-enabled and
free-threaded build, we suggest reading [the `ft_utils`
documentation](https://github.com/facebookincubator/ft_utils/blob/main/docs/ft_worked_examples.md)
on this topic.

## Suggested Plan of Attack

Below, we outline a plan of attack for updating a Python project to support the
free-threaded build. Since the changes required in native extensions are more
substantial, we have split off the guide for porting extension modules into
[a subsequent section](porting-extensions.md).

### Define and document thread safety guarantees

Consider adding a section to your documentation clearly documenting the thread
safety guarantees of your library. Note any use of global state as well as
whether the mutable data structures exposed by your library support sequentially
consistent shared concurrent use. You should document any locks that you expect
might impact multithreaded scaling for realistic workflows. Encourage user
feedback, particularly for reports of thread-unsafe behavior in code that is
documented to be thread-safe, as well as reports of poor multithreaded scaling
in code that you expect to scale well.

You can indicate the level of support for free-threading in your library by
adding a [trove classifier](https://pypi.org/classifiers/) to the metadata of
your package. The currently supported trove classifiers for this purpose are:

- `Programming Language :: Python :: Free Threading :: 1 - Unstable`
- `Programming Language :: Python :: Free Threading :: 2 - Beta`
- `Programming Language :: Python :: Free Threading :: 3 - Stable`
- `Programming Language :: Python :: Free Threading :: 4 - Resilient`

The numeric level of support in the classifier corresponds to the level of support. To give some guidance as to what that means:

1. For experimentation and feedback only.
1. Free threaded usage is supported, but documentation of constraints and limitations may be incomplete.
1. Supported for production use, multithreaded use is tested, and thread safety issues are clearly documented.
1. Fully supported and fully thread safe.

You can see how supporting the free-threaded build is not all all-or-nothing
thing. It is a perfectly valid choice to, for example, only support running on
the free-threaded build in effectively single-threaded contexts and not support
shared use of objects. It is then up to the users of your library to add locking
where appropriate or needed. The advantage of this choice is that it does not
force all consumers of your library to pay any cost associated with ensuring
thread safety.

### Thread Safety of Pure Python Code

The CPython interpreter protects you from low-level memory unsafety due to [data
races](https://en.wikipedia.org/wiki/Race_condition#Data_race). It does not
protect you from introducing thread safety issues due to [race
conditions](https://en.wikipedia.org/wiki/Race_condition). It is possible to
write algorithms that depend on the precise timing of threads completing
work. It is up to you as a user of multithreaded parallelism to ensure that
simultaneous reads and writes to the same Python variable are impossible.

Below we describe various approaches for improving the determinism of
multithreaded pure Python code. The correct approach will depend on exactly what
you are doing.

### General considerations for porting

Many projects assume the GIL serializes access to state shared between threads,
introducing the possibility of data races in native extensions and race
conditions that are impossible when the GIL is enabled.

We suggest focusing on safety and multithreaded scaling before single-threaded
performance.

Here's an example of this approach. If adding a lock to a global cache would harm
multithreaded scaling, and turning off the cache implies a small performance
hit, consider doing the simpler thing and disabling the cache in the
free-threaded build.

Single-threaded performance can always be improved later,
once you've established free-threaded support and hopefully improved test
coverage for multithreaded workflows.

NumPy, for example, decided *not* to add explicit locking to the ndarray object
and [does not support mutating shared
ndarrays](https://numpy.org/devdocs/reference/thread_safety.html#thread-safety). This
was a pragmatic choice given existing heavy multithreaded use of NumPy in the
GIL-enabled build and a desire to not introducing scaling bottlenecks in
existing workflows.

Eventually NumPy may need to offer explicitly thread-safe data structures, but
it is a valid choice to initially support free-threading while still exposing
possibly unsafe operations if users use the library unsafely.

For your libraries, we suggest to focus on thread safety issues that only occur
with the GIL disabled. Any non-critical pre-existing thread safety issues can be
dealt with later once the free-threaded build is used more. The goal for your
initial porting effort should be to enable further refinement and
experimentation by fixing issues that prevent using the library at all.

## Multithreaded Python Programming

The Python standard library offers a rich API for multithreaded
programming. This includes the [`threading`
module](https://docs.python.org/3/library/threading.html), which offers
relatively low-level locking and synchronization primitives, as well as the
[`queue module`](https://docs.python.org/3/library/queue.html) for safe
communication between threads, and the
[`ThreadPoolExecutor`](https://docs.python.org/3/library/concurrent.futures.html#concurrent.futures.ThreadPoolExecutor)
high-level thread pool runner.

If you'd like to learn more about multithreaded Python programming in the
GIL-enabled build, Santiago Basulto's [tutorial from PyCon
2020](https://www.youtube.com/watch?v=18B1pznaU1o) is a good place to start.

For a pedagogical introduction to multithreaded programming in free-threaded
Python, we suggest reading the
[`ft_utils`](https://github.com/facebookincubator/ft_utils/blob/main/docs/index.md)
documentation, particularly the section on [the impact of the global interpreter
lock on multithreaded Python
programs](https://github.com/facebookincubator/ft_utils/blob/main/docs/ft_worked_examples.md#understanding-the-global-interpreter-lock-gil-and-its-impact-on-multithreaded-python-programs). Many
pure Python operations are not atomic and are susceptible to race conditions, or
only appear to be thread-safe in the GIL-enabled build because of details of how
CPython releases the GIL in a round-robin fashion to allow threads to run.

### Dealing with mutable global state

The most common source of thread safety issues in Python packages is use of
global mutable state. Many projects use module-level or class-level caches to
speed up execution but do not envision filling the cache simultaneously from
multiple threads. See the [testing guide](testing.md) for strategies to add
tests to detect problematic global state.

For example, the `do_calculation` function in the following module is not
thread-safe:

```python
from internals import _do_expensive_calculation

global_cache = {}


def do_calculation(arg):
    if arg not in global_cache:
        global_cache[arg] = _do_expensive_calculation(arg)
    return global_cache[arg]
```

If `do_calculation` is called simultaneously in multiple threads, then it is
possible for at least two threads to see that `global_cache` doesn't have the
cached key and call `_do_expensive_calculation`. In some cases this is harmless,
but depending on the nature of the cache, this could lead to unnecessary network
access, resource leaks, or wasted unnecessary compute cost.

### Converting global state to thread-local state

One way of dealing with issues like this is to convert a shared global cache
into a thread-local cache. In this approach, each thread will see its own private
copy of the cache, making races between threads impossible. This approach makes
sense if having extra copies of the cache in each thread is not prohibitively
expensive or does not lead to excessive runtime network, CPU, or memory use.

In pure Python, you can create a thread-local cache using an instance of
[threading.local](https://docs.python.org/3/library/threading.html#thread-local-data). Each
thread will see independent versions of the thread-local object. You could
rewrite the above example to use a thread-local cache like so:

```python
import threading

from internals import _do_expensive_calculation

local = threading.local()

local.cache = {}


def do_calculation(arg):
    if arg not in local.cache:
        local.cache[arg] = _do_expensive_calculation(arg)
    return local.cache[arg]
```

This wouldn't help a case where each thread having a copy of the cache would be
prohibitive, but it does fix possible issues with resource leaks issues due to
races filling a cache.

### Making mutable global caches thread-safe with locking

If a thread-local cache doesn't make sense, then you can serialize access to the
cache with a lock. A
[lock](<https://en.wikipedia.org/wiki/Lock_(computer_science)>) provides exclusive
access to some resource by forcing threads to *acquire* a lock instance before
they can use the resource and *release* the lock when they are done. The lock
ensures that only one thread at a time can use the acquired lock - all other
threads [block execution](<https://en.wikipedia.org/wiki/Blocking_(computing)>)
until the thread that holds the lock releases it, at which point only one thread
waiting to acquire the lock is allowed to run.

You could rewrite the above thread-unsafe example to be thread-safe using a lock
like this:

```python
import threading

from internals import _do_expensive_calculation

cache_lock = threading.Lock()
global_cache = {}


def do_calculation(arg):
    if arg in global_cache:
        return global_cache[arg]

    with cache_lock:
        if arg not in global_cache:
            global_cache[arg] = _do_expensive_calculation(arg)
    return global_cache[arg]
```

Note that after acquiring the lock, we first check if the requested key
has been filled by another thread, to prevent unnecessary calls to
`_do_expensive_calculation` if another thread filled the cache while the thread
currently holding the lock was blocked on acquiring the lock. Also note that we
avoid using
[`Lock.acquire`](https://docs.python.org/3/library/threading.html#threading.Lock.acquire)
and [`Lock.release`](https://docs.python.org/3/library/threading.html#threading.Lock.release)
and instead we use the lock as a context manager. The difference is subtle: the context
manager calls `Lock.release` in a `try` ... `finally` clause, so if
`_do_expensive_calculation` were to raise an exception, this ensures that the lock won't
stay locked forever.

Note that acquiring the same lock recursively leads to deadlocks. Also,
in general, it is possible to create a deadlock in any program with more than
one lock. Care must be taken to ensure that operations done while the lock is
held cannot lead to recursive calls or lead to a situation where a thread owning
the lock is blocked on acquiring a different mutex. You do not need to worry
about deadlocking with the GIL in pure Python code, the interpreter will handle
that for you.
There is also
[threading.RLock](https://docs.python.org/3/library/threading.html#rlock-objects),
which provides a reentrant lock allowing threads to recursively acquire the same
lock.

Finally, note how the above code will ensure that only a single call to
`_do_expensive_calculation` will run at any given time, regardless of `arg`.
This may not be desirable; one would want to allow calling the function in
parallel for different arguments. In that case, you need a separate lock for each
`arg` - but you also need a global lock to manage your collection of locks!

```python
import threading

from internals import _do_expensive_calculation

cache_locks_lock = threading.Lock()
cache_locks = {}
global_cache = {}


def do_calculation(arg):
    if arg in global_cache:
        return global_cache[arg]

    with cache_locks_lock:
        # Note: setdefault() is not atomic!
        lock = cache_locks.setdefault(threading.Lock())

    lock.acquire()
    try:
        if arg not in global_cache:
            global_cache[arg] = _do_expensive_calculation(arg)
    finally:
        lock.release()
        # Ignore a potential double deletion.
        # Don't assume `cache_locks.pop(arg)` to be thread-safe.
        try:
            del cache_locks[arg]
        except KeyError:
            pass

    return global_cache[arg]
```

### Raising errors under shared concurrent use.

Sometimes it's a programming error to share an object between threads. An
example might be a wrapper for a low-level C compression library that does not
support sharing compression contexts between threads. You could make it so users
see an error at runtime when they try to share a compression context like this:

```python
from dataclasses import dataclass


@dataclass
class CompressionContext:
    lock: threading.Lock
    state: _LowLevelCompressionContext

    def compress(self, data):
        if not self.lock.acquire(blocking=False):
            raise RuntimeError("Concurrent use detected!")
        try:
            self.state.compress(data)
        finally:
            self.lock.release()
```

This does require paying the cost of acquiring and releasing a mutex, but
because no thread ever blocks on acquiring the lock, this thread cannot
introduce hidden multithreaded scaling issues.

## Dealing with thread-unsafe objects

Mutability of objects is deeply embedded in the Python runtime and many tools freely
assign to or mutate data stored in a python object.

In the GIL-enabled build, in many cases, you can get away with mutating a shared
object safely. This is true so long as whatever mutation you are attempting to
do is fast enough that a thread switch is very unlikely to happen while you are
doing work.

In the free-threaded build there is no GIL to protect against mutation of state
living on a Python object that is shared between threads. Just like when we used
a lock to protect a global cache, we can also use a per-object lock to serialize
access to state stored in a Python object. Consider the following class:

```python
import time
import random


class RaceyCounter:
    def __init__(self):
        self.value = 0

    def increment(self):
        current_value = self.value
        time.sleep(random.randint(0, 10) * 0.0001)
        self.value = current_value + 1
```

Here we're simulating doing an in-place addition on an expensive function. A
real example might have a method that looks something like this:

```python
def increment(self):
    self.value += do_some_expensive_calulation()
```

If we run this example in a thread pool, you'll see that the answer you get will
vary randomly depending on the timing of the sleeps:

```python
from concurrent.futures import ThreadPoolExecutor

counter = RaceyCounter()


def closure(counter):
    counter.increment()


with ThreadPoolExecutor(max_workers=8) as tpe:
    futures = [tpe.submit(closure, counter) for _ in range(1000)]
    for f in futures:
        f.result()

print(counter.value)
```

On both the free-threaded and GIL-enabled build, you will see the output of this
script randomly vary.

We can ensure the above script has deterministic answers by adding a lock to our counter:

```python
import threading


class SafeCounter:
    def __init__(self):
        self.value = 0
        self.lock = threading.Lock()

    def increment(self):
        with self.lock:
            current_value = self.value
            time.sleep(random.randint(0, 10) * 0.0001)
            self.value = current_value + 1
```

If you replace `RaceyCounter` with `SafeCounter` in the script above, it will
always output 1000.

Of course this introduces a scaling bottleneck when `SafeCounter` instances are
concurrently updated. It's possible to implement more optimized locking
strategies, but doing so requires knowledge of the problem.

### Third-party libraries

Both the [`ft_utils`](https://github.com/facebookincubator/ft_utils) and
[`cereggii`](https://github.com/dpdani/cereggii) libraries offer data structures
that add enhanced atomicity or improved multithreaded scaling compared with
standard library primitives.

## Dependencies that don't support free-threading

If one of your package's dependencies do not support free-threading, you might
be able to switch to a fork that does. Find more details in
[our guidance for handling dependencies that don't support free-threading](dependencies.md).

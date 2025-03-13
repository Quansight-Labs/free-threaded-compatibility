# Porting Python Packages to Support Free-Threading

Many Python packages, particularly packages relying on C extension modules, are
not thread-safe in the free-threaded build as of mid-2024. Up until now, the GIL
has added implicit locking around any operation in Python or C that holds the
GIL, and the GIL must be explicitly dropped before many thread safety issues
become problematic. Also, because of the GIL, attempting to parallelize many
workflows using the Python
[threading](https://docs.python.org/3/library/threading.html) module will not
produce any speedups, so thread safety issues that are possible even with the
GIL are not hit often since users do not make use of threading as much as other
parallelization strategies. This means many codebases have threading bugs that
up-until-now have only been theoretical or present in niche use cases. With
free-threading, many more users will want to use Python threads.

This means we must analyze Python codebases to identify supported and
unsupported multithreaded workflows and make changes to fix thread safety
issues. This need is particularly acute for low-level code exposed to Python
including C, C++, Cython, and Rust code exposed to Python, but even pure-python
codebases can exhibit thread safety issues in the free-threaded build that are
either very unlikely or impossible in the default configuration of the
GIL-enabled build.

Below, we outline a plan of attack for updating a Python project to support the
free-threaded build. Since the changes required in native extensions are more
substantial, we have split off the guide for porting extension modules into the
[next section](porting-extensions.md).

## Suggested Plan of Attack

### Thread Safety of Pure Python Code.

Free-threading is implemented in CPython such that pure Python code is
thread-safe, at least to the same extent as it is with the GIL enabled today. We
use "thread-safe" here to mean that CPython should not crash running
multithreaded pure python code, not necessarily that a multithreaded program
will always produce deterministic results. It is up to the author of a program,
application, or library to ensure safe multithreaded usage when using the
library in a supported manner.

There are a few ways you can create thread safety issues in your own
code. The most common ones are: using global state for configuration or other
purposes, implementing a cache with a dict or other variable not meant for that
purpose, or using functionality of a dependency that itself isn't
thread-safe. If your package does none of those things, you are very likely
ready for free-threading already.

What gets trickier is testing whether your package is thread-safe. For that
you'll need multi-threaded tests, and that can be more involved - see [our guide
to adding multithreaded test coverage](testing.md) to Python packages.

### General considerations for porting

Many projects assume the GIL serializes access to state shared between threads,
introducing the possibility of data races in native extensions and race
conditions that are impossible when the GIL is enabled.

We suggest focusing on safety over single-threaded performance. For example, if
adding a lock to a global cache would harm multithreaded scaling, and turning
off the cache implies a small performance hit, consider doing the simpler
thing and disabling the cache in the free-threaded build. Single-threaded
performance can always be improved later, once you've established free-threaded
support and hopefully improved test coverage for multithreaded workflows.

NumPy, for example, decided *not* to add explicit locking to the ndarray object
and [does not support mutating shared
ndarrays](https://numpy.org/devdocs/reference/thread_safety.html#thread-safety). This
was a pragmatic choice given existing heavy multithreaded use of NumPy in the
GIL-enabled build and a desire to not introducing scaling bottlenecks in
existing workflows.

Eventually NumPy may need to offer explicitly thread-safe data structures, but
it is a valid choice to initially support free-threading while still exposing
possibly unsafe operations if users use the library unsafely.

For pure-python packages, the unsafety would usually result in unexpected
exceptions or silently incorrect results. Projects shipping extension modules
might see crashes.

For your libraries, we suggest to focus on thread safety issues that only occur
with the GIL disabled. Any non-critical preexisting thread safety issues can be
dealt with later once the free-threaded build is used more. The goal for your
initial porting effort should be to enable further refinement and
experimentation by fixing issues that prevent using the library at all.

## Multithreaded Python Programming

The Python standard library offers a rich API for multithreaded
programming. This includes the [`threading`
module](https://docs.python.org/3/library/threading.html), which offers
relatively low-level locking and synchronization primitives, as well as the
[`queue module`](https://docs.python.org/3/library/queue.html) and the
[`ThreadPoolExecutor`](https://docs.python.org/3/library/concurrent.futures.html#concurrent.futures.ThreadPoolExecutor)
high-level thread pool interface.

For a pedagogical introduction to multithreaded programming in free-threaded
Python, we suggest reading the
[`ft_utils`](https://github.com/facebookincubator/ft_utils/blob/main/docs/index.md)
documentation, particularly the section on [the impact of the global interpreter
lock on multithreaded Python
programs](https://github.com/facebookincubator/ft_utils/blob/main/docs/ft_worked_examples.md#understanding-the-global-interpreter-lock-gil-and-its-impact-on-multithreaded-python-programs). Many
pure Python operations are not atomic and are susceptible to race conditions, or
only appear to be thread-safe because of the timing of the GIL's default
thread-switch interval.

Both the [`ft_utils`](https://github.com/facebookincubator/ft_utils) and
[`cereggii`](https://github.com/dpdani/cereggii) libraries offer data structures
that add enhanced atomicity to standard library primitives. We hope these sorts
of tools to aid concurrent free-threaded programming continue to pop up and
evolve, as they will be key to enabling scalable multithreaded workflows.

If you'd like to learn more about multithreaded Python programming, Santiago
Basulto's [tutorial from PyCon
2020](https://www.youtube.com/watch?v=18B1pznaU1o) is a good place to start.

## Dealing with mutable global state

The most common source of thread safety issues in Python packages is use of
global mutable state. Many projects use module-level or class-level caches to
speed up execution but do not envision filling the cache simultaneously from
multiple threads.

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
into a thread-local cache. In this apprach, each thread will see its own private
copy of the cache, making races between threads impossible. This approach makes
sense if having extra copies of the cache in each thread is not prohibitively
expensive or does not lead to excessive runtime network, CPU, or memory use.

In pure Python, you can create a thread-local cache using an instance of
[threading.local](https://docs.python.org/3/library/threading.html#thread-local-data). Each
thread will see independent versions of the thread-local object. You could rewrite the above example
to use a thread-local cache like so:

```
import threading

from internals import _do_expensive_calculation

local = threading.local()

local.cache = {}

def do_calculation(arg):
    if arg not in local.cache:
        local.cache[arg] = _do_expensive_calculation(arg)
    return local.cache[arg]
```

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

```
import threading

from internals import _do_expensive_calculation

cache_lock = threading.Lock()
global_cache = {}

def do_calculation(arg):
    if arg in global_cache:
        return global_cache[arg]

    cache_lock.acquire()
    if arg not in global_cache:
        global_cache[arg] = _do_expensive_calculation(arg)
    cache_lock.release()
    return global_cache[arg]

```

Note that after acquiring the lock, we first check if the requested key
has been filled by another thread, to prevent unnecessary calls to
`_do_expensive_calculation` if another thread filled the cache while the thread
currently holding the lock was blocked on acquiring the lock. Also note that
[`Lock.acquire`](https://docs.python.org/3/library/threading.html#threading.Lock.acquire)
*must* be followed by a call to
[`Lock.release`](https://docs.python.org/3/library/threading.html#threading.Lock.release),
calling `Lock.acquire()` recursively on the same lock leads to deadlocks. Also,
in general, it is possible to create a deadlock in any program with more than
one lock. Care must be taken to ensure that operations done while the lock is
held cannot lead to recursive calls or lead to a situation where a thread owning
the lock is blocked on acquiring a difference mutex. You do not need to worry
about deadlocking with the GIL in pure Python code, the interpreter will handle
that for you.

There is also
[threading.RLock](https://docs.python.org/3/library/threading.html#rlock-objects),
which provides a reentrant lock allowing threads to recursively acquire the same
lock.
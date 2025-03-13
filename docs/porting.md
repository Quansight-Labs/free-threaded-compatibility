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

### Validating thread safety with testing

Put priority on thread safety issues surfaced by real-world testing. Run the
test suite for your project and fix any failures that occur only with the GIL
disabled. Some issues may be due to changes in Python 3.13 that are not
specific to the free-threaded build.

If you are unable to run your package with the GIL disabled because of problems
in extension modules or in dependencies, you can still test with the GIL enabled
by lowing the [thread switch interval](<>) to a very small value (e.g. a
microsecond or shorter). You can call \[`sys.setswitchiterval`\] before running
multithreaded tests to force Python to release the GIL more often that the
default configuration. This can expose thread safety issues that the GIL is
masking.

Unless your tests make heavy use of the `threading` module, you will likely not
hit many issues, so also consider constructing multithreaded tests to expose
bugs based on workflows you want to support. Issues found in these tests are the
issues your users will most likely hit first.

Multithreaded Python programs can exhibit [race
conditions](https://en.wikipedia.org/wiki/Race_condition) which produce random
results depending on the order of execution in a multithreaded context. This can
happen even with the GIL providing locking, so long as the algorithm releases
the GIL at some point, and many Python operations can lead to the GIL being
released at some point. If your library was not designed with multithreading in
mind, it is likely that some form of locking or synchronization is necessary to
make mutable data structures defined by your library thread-safe. You should
document the thread-safety guarantees of your library, both with and without the
GIL.

You should focus your efforts on analyzing the safety of shared use of mutable
data structures or mutable global state. Decide whether it is supported and to
what level it is supported to share mutable state between threads. It is a valid
choice to leave it up to users to add synchronization, with the proviso that
thread-unsafe data structures should be clearly documented as such.

Generally global mutable state is not safe in the free-threaded build without
some form of locking. Many projects use global mutable state (e.g. module-level
state) for convenience with the assumption that the GIL provides locking on the
state. That will most likely not be valid without some form of locking on the
free-threaded build. It is also likely that there are thread safety issues
related to use of global state even in the GIL-enabled build. See the section
below on [global state in tests](porting.md#fixing-thread-unsafe-tests)
for more information about updating test suites to work with the free-threaded
build.

You can look at
[pytest-run-parallel](https://github.com/Quansight-Labs/pytest-run-parallel) as
well as
[pytest-freethreaded](https://github.com/tonybaloney/pytest-freethreaded), which
both offer pytest plugins to enable running tests in an existing `pytest` test
suite simultaneously in many threads, with the goal of validating thread
safety. [unittest-ft](https://github.com/amyreese/unittest-ft) offers similar
functionality for running `unittest`-based tests in parallel.

These plugins are useful for discovering issues related to use of global state,
but cannot discover issues from multithreaded use of data structures defined by
your library.

If you would like to create your own testing utilities, the
[`concurrent.futures.ThreadPoolExecutor`](https://docs.python.org/3/library/concurrent.futures.html#concurrent.futures.ThreadPoolExecutor)
class is a lightweight way to create multithreaded tests where many threads
repeatedly call a function simultaneously. You can also use the `threading`
module directly for more complicated multithreaded test workflows. Adding a
`threading.Barrier` before a line of code that you suspect will trigger a race
condition is a good way to synchronize workers and increase the chances that an
infrequent test failure will trigger.

NumPy makes use of the following helper function to enable writing explicitly
multithreaded tests, with a number of useful features to generically set up
different testing scenarios:

```python
from concurrent.futures import ThreadPoolExecutor
import threading


def run_threaded(
    func,
    num_threads=8,
    pass_count=False,
    pass_barrier=False,
    outer_iterations=1,
    prepare_args=None,
):
    """Runs a function many times in parallel"""
    for _ in range(outer_iterations):
        with ThreadPoolExecutor(max_workers=num_threads) as tpe:
            if prepare_args is None:
                args = []
            else:
                args = prepare_args()
            if pass_barrier:
                barrier = threading.Barrier(num_threads)
                args.append(barrier)
            if pass_count:
                all_args = [(func, i, *args) for i in range(num_threads)]
            else:
                all_args = [(func, *args) for i in range(num_threads)]
            try:
                futures = []
                for arg in all_args:
                    futures.append(tpe.submit(*arg))
            finally:
                if len(futures) < num_threads and pass_barrier:
                    barrier.abort()
            for f in futures:
                f.result()
```

Using this helper, you could write a multithreaded test using a shared list like this:

```python
def test_parallel_append():
    shared_list = []

    def closure(i, b):
        b.wait()
        shared_list.append(i)

    run_threaded(closure, num_threads=8, pass_barrier=True, pass_count=True)

    assert sum(shared_list) == sum(range(8))
```

Generally multithreaded tests look something like the above: define a closure
that operates on (possibly) shared data, spawn a thread pool that runs the
closure in many threads, and assert something about the state of the world
either inside the closure or after the thread pool finishes running. The
assertion might be merely that a crash doesn't happen, in which case no explicit
asserts are necessary.

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
and [does not support mutating shared ndarrays](<>). This was a pragmatic choice
given existing heavy multithreaded use of NumPy in the GIL-enabled build and a
desire to not introducing scaling bottlenecks in existing workflows.

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
pure Python operation are not atomic and are susceptible to race conditions, or
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

Note that the lock after acquiring the lock, we first check if the requested key
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

## Fixing thread-unsafe tests.

Many existing tests are written using global state. This is not a problem if the
test only runs once, but if you would like to use your tests to check for
possible thread safety issues by running existing tests on many threads, you
will likely need to update the tests to eliminate use of global state.

Since tests using global state are inherently racey, this means that test
failures associated with these tests are also inherently flakey. If you see
tests failing intermittently, you should not discount that you are using global
state in a test, or even inadvertently using global state in `pytest` itself.

#### `pytest` is not thread-safe

See [the `pytest`
docs](https://docs.pytest.org/en/stable/explanation/flaky.html#thread-safety)
for more information about this. While tests can manage their own threads, you
should not assume that functionality provided by `pytest` is thread-safe.

Functionality that is known not to be thread-safe includes:

- [`pytest.warns`](https://docs.pytest.org/en/stable/reference/reference.html#pytest.warns),
    it relies on `warnings.catch_warnings`, which is not thread-safe.
- The [`tmp_path`](https://docs.pytest.org/en/stable/reference/reference.html#std-fixture-tmp_path)
    and [`tmpdir`](https://docs.pytest.org/en/stable/reference/reference.html#std-fixture-tmpdir)
    fixtures, since they rely on the filesystem
- The [`capsys`
    fixture](https://docs.pytest.org/en/stable/reference/reference.html#std-fixture-capsys),
    because of shared use of `sys.stdout` and `sys.stderr`.
- The [`monkeypatch`
    fixture](https://docs.pytest.org/en/stable/reference/reference.html#std-fixture-monkeypatch).

Note that the `pytest` maintainers have explicitly ruled out making `pytest`
thread-safe, please do not open issues asking to fix thread safety issues in
`pytest` itself.

#### The `warnings` module is not thread-safe

Many tests carefully ensure that warnings will be seen by the user in cases
where the library author intends users to see them. These tests inevintably make
use of the [`warnings`
module](https://docs.python.org/3/library/warnings.html). As noted in [the
documentation for
`warnings.catch_warnings`](https://docs.python.org/3/library/warnings.html#available-context-managers),
the functionality provided by Python to track warnings is inherently
thread-unsafe. This means tests that check for warnings should be marked as
thread-unsafe and should be skipped when running tests on many threads
simultaneously, since they will randomly pass or fail depending on thread
timing.

Hopefully in the future it will be possible for Python to write a scalable
infrastucture for tracking warnings to fix this issue once and for all. See [the
CPython issue](https://github.com/python/cpython/issues/91505) tracking this
problem for more information.

#### File system thread safety

Many tests make use of the file system, either via a temporary file, or by
simply directly writing to the folder running the test. If the filename used by
the test is a constant or it is ever shared between instances of the test, the
filesystem becomes shared global state, and the test will not be thread-safe.

The easiest way to fix this is to use
[`tempfile`](https://docs.python.org/3/library/tempfile.html), which
automatically handles generating file handles in a thread-safe manner. If for
some reason this isn't practical, consider forcing the filenames used in tests
to be unique, for example by appending a
[UUID](https://docs.python.org/3/library/uuid.html) to the filename.

#### Hypothesis is not thread-safe

The details of this are [spelled
out](https://hypothesis.readthedocs.io/en/latest/details.html#thread-safety-policy)
in the Hypothesis documentation. Similar to Pytest, it should be safe to spawn
helper threads in a hypothesis test and pass data generated by hypothesis into
those threads, so long as the use of helper threads does not change the order in
which hypothesis generates test data or exhibits non-deterministic behavior. It
is also not safe to interact with the Hypothesis API simultaneously from multiple
threads.

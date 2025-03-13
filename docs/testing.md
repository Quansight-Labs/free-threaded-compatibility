# Validating thread safety with testing

Put priority on thread safety issues surfaced by real-world testing. Run the
test suite for your project and fix any failures that occur only with the GIL
disabled. Some issues may be due to changes in Python 3.13 that are not
specific to the free-threaded build.

If you are unable to run your package with the GIL disabled because of problems
in extension modules or in dependencies, you can still test with the GIL enabled
by lowing the thread switch interval to a very small value (e.g. a microsecond
or shorter). You can call
[`sys.setswitchiterval`](https://docs.python.org/3/library/sys.html#sys.setswitchinterval)
before running multithreaded tests to force Python to release the GIL more often
that the default configuration. This can expose thread safety issues that the
GIL is masking.

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
or class-level state) for convenience with the assumption that the GIL provides
locking on the state. That will most likely not be valid without some form of
locking on the free-threaded build. It is also likely that there are thread
safety issues related to use of global state even in the GIL-enabled build. See
the section below on [global state in
tests](porting.md#fixing-thread-unsafe-tests) for more information about
updating test suites to work with the free-threaded build.

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

# Validating thread safety with testing

Put priority on thread safety issues surfaced by real-world testing. Run the
test suite for your project and fix any failures that occur only with the GIL
disabled. Some issues may be due to changes in Python 3.13 that are not
specific to the free-threaded build.

If you are unable to run your package with the GIL disabled because of problems
in extension modules or in dependencies, you can still test with the GIL enabled
by setting the thread switch interval to a very small value (e.g. a microsecond
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
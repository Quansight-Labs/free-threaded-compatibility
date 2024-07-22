# Uncovering concurrency issues, testing and debugging
Until now, the GIL has allowed developers to ignore C
safety issues when writing parallel programs, since the GIL ensured that
all thread execution was serialized simultaneous access
to Python objects and state defined in the interpreter. 
Under the new free-threaded
safe access to data from multiple C threads. This is particularly important in C extensions that assumed the GIL serialized access to static state in C programs.

Usually, concurrency issues arise when two or more threads try to modify the
same value in memory. In Python, this commonly occurs when a class or function
defines shared state, either via an attribute or a variable that can be modified
from each thread execution scope.

The most common issues related to concurrency in the context of free-threaded
Python are either dirty reads/writes to data, unexpected behavior due to
simultaneous access to native libraries that are not thread-safe, and finally,
major runtime crashes due to memory allocation issues and forbidden
pointer lookups. While the first case depends on the actual implementation of
the algorithm/routine and may produce unintended results, it would not cause
a fatal crash of the interpreter, as opposed to the last two cases.

In order to discover, handle and debug concurrency issues at large, there are
several strategies, which we will summarize next.

## Identify shared state objects.
First, we recommend to look for any singleton objects, which to due to their
nature, are 100% candidates for concurrency issues. Such objects usually
represent single interfaces to access data, such as caches, database connections
and native library wrappers.

Second, we advise to identify classes whose methods have side effects and
mutations of their attributes, which can be problematic at the moment of
introducing concurrent calls.

Depending on the performance and consistency requirements, serializing
mechanisms such as locks, barriers may be required, in other cases other lock-free
constructs like atomic variables may present an advantage, however, this depends
on the actual use case, requirements and constraints required by the program.

## Testing scenarios
In order to check that a function or class has no concurrency issues, it is
necessary to define test functions that cover such cases. For such scenarios, the
standard `threading` library defines several low-level parallel primitives that
can be used to test for concurrency, while the `concurrent.futures` module
provides high-level constructs.

For example, consider a method `MyClass.call_unsafe`
that has been flagged as having concurrency issues since it mutates attributes
of a shared object that is accessed by multiple threads. We can write a test for
it using first low-level primitives:

```python
"""test_concurrent.py"""

# Low level parallel primitives
import threading
# High level parallel constructs
from concurrent.futures import ThreadPoolExecutor
# Library to test
from mylib import MyClass


def test_call_unsafe_concurrent_threading():
    # Defines a thread barrier that will be spawned before parallel execution
    # this increases the probability of concurrent access clashes.
    n_threads = 10
    barrier = threading.Barrier(n_threads)

    # This object will be shared by all the threads.
    cls_instance = MyClass(...)

    results = []
    def closure():
        # Ensure that all threads reach this point before concurrent execution.
        barrier.wait()
        r = cls_instance.call_unsafe()
        results.append(r)

    # Spawn n threads that call call_unsafe concurrently.
    workers = []
    for _ in range(0, n_threads):
        workers.append(threading.Thread(
            target=closure))

    for worker in workers:
        worker.start()

    for worker in workers:
        worker.join()

    # Do something about the results
    assert check_results(results)


def test_call_unsafe_concurrent_pool():
    # Defines a thread barrier that will be spawned before parallel execution
    # this increases the probability of concurrent access clashes.
    n_threads = 10
    barrier = threading.Barrier(n_threads)

    # This object will be shared by all the threads.
    cls_instance = MyClass(...)

    def closure():
        # Ensure that all threads reach this point before concurrent execution.
        barrier.wait()
        r = cls_instance.call_unsafe()
        return r

    with ThreadPoolExecutor(max_workers=n_threads) as executor:
        futures = [executor.submit(closure) for _ in range(n_threads)]

    results = [f.result() for f in futures]

    # Do something about the results
    assert check_results(results)
```

Given the non-deterministic nature of parallel execution, such tests may pass
from time to time. In order to reliably ensuring their failure under concurrency,
we recommend using `pytest-repeat`, which enables the `--count` flag in the
`pytest` command:

```bash
# Setting PYTHON_GIL=0 ensures that the GIL is effectively disabled.
PYTHON_GIL=0 pytest -x -v --count=100 test_concurrent.py
```

We advise to set `count` in the order of hundreds and even larger, in order to
ensure at least one concurrent clash event.


## Debugging tests that depend on native calls
If your code has native dependencies, either via C/C++ or Cython, `gdb`
(or `lldb`) can be used as follows:

```bash
# Setting PYTHON_GIL=0 ensures that the GIL is effectively disabled.
PYTHON_GIL=0 gdb --args python my_program.py --args ...

# To test under pytest
PYTHON_GIL=0 gdb --args python -m pytest -x -v "test_here.py::TestClass::test_method"
```

When Python is run under `gdb`, several Python integration commands will be
available, such commands start with the `py-` prefix. For instance, the `py-bt`
allows to obtain a Python interpreter backtrace whenever the debugger hits a native
frame, this allows to improve the tracking of execution between Python and native
frames.

### Cython debugging
Since Cython produces intermediate C/C++ sources that then are compiled into native
code, stepping through may get difficult if done solely from the C source file.
In order to get through such difficulty, Cython includes the `cygdb` extension,
which enables `gdb` to go through large sections of C code that are equivalent to
a single Cython declaration.

Enabling `cygdb` requires the compilation of Cython sources with the `--gdb`
flag. After the sources are compiled and linked, it can be used as follows:

```bash
# For example, running the tests of scikit-image.
# build/cp313td/ contains the trace files generated by Cython to be compatible
# with cygdb
PYTHON_GIL=0 cygdb build/cp313td/ -- --args python -m  pytest -x -v skimage/
```

Since `cygdb` requires the Python interpreter version used to compile `gdb`
to match the one to be used during the execution of the script, recompiling `gdb`
will be necessary in order to ensure the most complete debugging experience.
We recommend the `gdb` [compilation instructions](https://www.linuxfromscratch.org/blfs/view/svn/general/gdb.html)
provided by the Linux from scratch project.

`cygdb` defines a set of commands prefixed by `cy` that replace the usual `gdb`
commands. For example `cy run` will start the program with the Cython debugging
extensions enabled, `cy break` will define a breakpoint on a function with the
Cython definition name, `cy next` will step over a Cython line, which is equivalent
to several lines in the produced C code.

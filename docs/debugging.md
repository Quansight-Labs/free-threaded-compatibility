# Uncovering concurrency issues, testing and debugging
Until now, the GIL has allowed developers to ignore C
safety issues when writing parallel programs, since the GIL ensured that
all thread execution was serialized, allowing for simultaneous access
to Python objects and state defined in the interpreter.

The new free-threaded model ensures that Python code access originating from
other Python code frames is safe and is guaranteed to not produce any major
interpreter crash, as opposed to unrestricted C code access, which can
present any of the common C thread-safety issues.

Usually, concurrency issues arise when two or more threads try to modify the
same value in memory. In Python, this commonly occurs when a class or function
defines native shared state, either via an attribute or a variable that can be
modified from native code in each thread execution scope.

The most common issues related to concurrency in the context of free-threaded
CPython extensions are either dirty reads/writes to global/shared C state,
unexpected behavior due to simultaneous access to C calls that are not
thread-safe, and finally, major runtime crashes due to memory allocation
issues and forbidden pointer lookups. While the first case depends on the
actual implementation of the algorithm/routine and may produce unintended
results, it would not cause a fatal crash of the interpreter, as opposed
to the last two cases.

In order to discover, handle and debug concurrency issues at large, there are
several strategies, which we will summarize next.

## Ensure that an extension module is free-threaded compliant
We highly suggest reading the detailed guide presented on
[Porting Extension Modules to Support Free-Threading](porting.md)

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

# Using LLDB (under LLVM/clang)
PYTHON_GIL=0 lldb -- $(which python) my_program.py

# Using LLDB (and pyenv)
PYTHON_GIL=0 lldb -- $(pyenv which python) $(pyenv which pytest) -x -v "test_here.py::TestClass::test_method"
```

When Python is run under `gdb`, several Python integration commands will be
available, such commands start with the `py-` prefix. For instance, the `py-bt`
allows to obtain a Python interpreter backtrace whenever the debugger hits a native
frame, this allows to improve the tracking of execution between Python and native
frames[^1].

For more information about `gdb` and `lldb` commands, we encourage reading
the [GDB to LLDB command map](https://lldb.llvm.org/use/map.html) page in the
official LLVM docs.

[^1]: This feature is not correctly working on `lldb` after CPython 3.12.

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

### Detecting issues in CPython
If a debugging session suggests that an error/bug is incoming from CPython,
we recommend installing a debug instance. The easiest way to accomplish this
is via `pyenv`:

```bash
pyenv install --debug --keep 3.13t-dev
```

This command will not only install a debug distribution of CPython, but also
will ensure that the source files are kept as well, such files will be loaded
by `gdb`/`lldb` at the moment of debugging. For more information regarding
CPython installation sources, please visit the
[Installing a free-threaded Python](installing_cpython.md) page.

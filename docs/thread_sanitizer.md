# Using Thread Sanitizer to validate and test thread safety

[Thread sanitizer](https://clang.llvm.org/docs/ThreadSanitizer.html) (or TSan)
is part of the compiler sanitizer suite, originally developed at Google and now
integrated with the LLVM and GCC compilers. The sanitizers instrument compiled
code with additional runtime checks for common sources of [undefined
behavior](https://en.wikipedia.org/wiki/Undefined_behavior).

Thread Sanitizer specializes in finding data races, a form of undefined behavior
that are possible in low-level multithreaded code. While Rust has compile-time
guarantees to prevent most data races, C and C++ do not prevent data races from
occurring and in practice many C and C++ extensions exhibit data races while
adding support for the free-threaded build.

## Compiling CPython and foundational packages with Thread Sanitizer

In this section we provide the commands to build a free-threading compatible
CPython interpreter and packages with TSan and other hints to discover potential
data races.

### `cpython_sanity` docker images

To ease working with thread sanitizer in projects that use Python, NumPy, and
SciPy, we have created a set of docker images that contain a pre-built Python
interpreter and common dependencies with thread sanitizer which can be
tricky to build.

See [the `cpython_sanity`
repository](https://github.com/nascheme/cpython_sanity) for more information
about how to use the docker images. Also see [NumPy PR #28808](https://github.com/numpy/numpy/pull/28808/files),
which adjusted NumPy TSan CI to use the `ghcr.io/nascheme/numpy-tsan:3.14t-dev`
docker image instead of building Python from source, saving ten minutes of
compute time per CI run.

### Compile free-threaded CPython with TSan

- Clone the latest stable branch (`3.14`):

```bash
git clone https://github.com/python/cpython.git -b 3.14
```

- Configure and build the interpreter. Below instructions are for Linux
    (Windows and macOS may require some changes). We skip the instructions on how
    to install the Clang compiler.

```bash
cd cpython
CC=/path/to/clang CXX=/path/to/clang++ ./configure --disable-gil --with-thread-sanitizer --prefix $PWD/cpython-tsan
make -j 8
make install
```

- To use the built Python interpreter:

```bash
# Create a virtual environment:
$PWD/cpython-tsan/bin/python3.14t -m venv ~/tsanvenv

# Then activate it:
source ~/tsanvenv/bin/activate

# Exit the `cpython` folder (preparation for the next step below)
cd ..
```

If you use pyenv, you can also enable a thread sanitizer build with `pyenv install` like so:

```bash
CC=/path/to/clang CXX=/path/to/clang++ CONFIGURE_OPTS="--with-thread-sanitizer" pyenv install 3.14t-dev
```

And then activate the build with e.g. `pyenv local 3.14t-dev`.

!!! note

    On MacOS, you may see messages like this when you start Python:

    ```
    python(7027,0x1f6dfc240) malloc: nano zone abandoned due to inability to reserve vm space.
    ```

    This message is being emitted by the MacOS malloc implementation. As
    [explained
    here](https://stackoverflow.com/questions/64126942/malloc-nano-zone-abandoned-due-to-inability-to-preallocate-reserved-vm-space),
    this happens for any program compiled with TSan on MacOS and can
    be safely ignored by setting the `MallocNanoZone` environment variable to
    0\. You should only set this in the session you are running TSan
    under, as this setting will slow down other programs that allocate memory.

### Compile NumPy with TSan

- Get the source code (for example, the `main` branch)

```bash
git clone --recursive https://github.com/numpy/numpy.git
```

- Install the build requirements:

```bash
cd numpy
python -m pip install -r requirements/build_requirements.txt
```

- Build the package

```bash
CC=/path/to/clang CXX=/path/to/clang++ python -m pip install -v . --no-build-isolation -Csetup-args=-Db_sanitize=thread
# or with debug info
# CC=/path/to/clang CXX=/path/to/clang++ python -m pip install -v . --no-build-isolation -Csetup-args=-Db_sanitize=thread -Csetup-args=-Dbuildtype=debugoptimized
```

## TSan suppressions

While TSan is incredibly useful, it can also be difficult to securely fix all
races detected by TSan. Some races are also more impactful than others. To avoid
drowning out new issues with existing issues found under TSan testing, it's
common practice to create a [suppressions
file](https://github.com/google/sanitizers/wiki/ThreadSanitizerSuppressions) for
known issues and point TSan at the suppressions when you run it.

Here's an example suppression file from the TSan docs:

```
race:llvm::RuntimeDyldELF::registerEHFrames
race:partial_vectorcall_fallback
race:dnnl_sgemm
```

This suppressions file tells TSan to not any races it detects in the functions
`llvm::RuntimeDyldELF::registerEHFrames`, `partial_vectorcall_fallback`, and
`dnnl_sgemm`.

You can tell TSan to use your suppressions file by setting `suppressions` in
`TSAN_OPTIONS`:

```
TSAN_OPTIONS="suppressions=$PWD/tsan-suppressions" python my_test.py
```

This would use a suppressions file name `tsan-suppressions` located in the
current directory.

### Using suppressions files from other projects

Depending on what you are doing, you may see races coming from code outside of your project, including from CPython itself.

There are known races in CPython that are tracked in a suppressions file used
for TSan testing in the CPython CI. You can see the version of this file in the
3.13 branch of CPython
[here](https://github.com/python/cpython/blob/3.13/Tools/tsan/suppressions.txt)
and the 3.14 branch
[here](https://github.com/python/cpython/blob/3.14/Tools/tsan/suppressions.txt). This
file might be a good place to start for your own testing, but you should make sure the suppressions file you are using corresponds to the versions of CPython you are using.

In addition to CPython, we are aware of the following projects that run tests in CI with TSan and use suppressions:

- NumPy ([TSan Suppressions](https://github.com/numpy/numpy/blob/main/tools/ci/tsan_suppressions.txt))
- CFFI ([TSan Suppressions](https://github.com/python-cffi/cffi/blob/b4bbe7940d3f76027534db1aecbae9b61c35221a/suppressions_free_threading.txt))

If you are aware of other suppression files used for TSan testing of Python
projects, please add them here.

### Reporting TSan issues in your dependencies

It is possible, or even likely in cases where TSan testing has not been used
before, that you will see races coming code in your dependencies. If you've
found a race in a project that already does TSan testing, then just go ahead and
make a bug report including the TSan race report and steps to reproduce the race.

If your dependency does not yet regularly test with TSan, consider adding
additional context and link to this guide to help the project understand what
they need to do to reproduce your report and to understand how important a
bugfix is.

## Running Python under TSan

If you have successfully compiled CPython and your project and any dependencies
with native extensions using TSan instrumentation, you should be able to run a
test script or your unit tests as normal. You will likely want to customize your
TSan testing with some options. We explain how to do that below.

### Useful TSan options

- By default, TSan reports warnings. To stop execution on the first TSan report,
    use:

```bash
TSAN_OPTIONS=halt_on_error=1 python -m pytest test.py
```

See [the TSan documentation](https://github.com/google/sanitizers/wiki/ThreadSanitizerFlags) for a full listing of options accepted by TSan.

### Running pytest tests under TSan

By default, pytest [captures all output from
tests](https://docs.pytest.org/en/stable/how-to/capture-stdout-stderr.html),
this means that you might only see output like `ThreadSanitizer: reported 2 warnings`, but with no accompanying report with details about the warning.

To ensure that pytest doesn't capture any output from TSan, you can
pass `-s` (short for `--show-capture`) to your pytest invocation.

Some authors of this guide have observed hangs running pytest with
`halt_on_error=1`. If you observe hangs, try setting `halt_on_error=0` in
TSAN_OPTIONS.

The [pytest-xdist](https://github.com/pytest-dev/pytest-xdist) plugin can also
sometimes be problematic if a test runner happens to crash during
execution. While `pytest-xdist` does have some support for detecting crashed
worker, it is not foolproof and the authors of this guide have observed hangs on
CI due to pytest-xdist not properly handling a worker failing due to a TSan
error.

The `pytest-xdist` plugin also [makes it impossible to obtain stdout from
a test runner](https://github.com/pytest-dev/pytest-xdist/issues/82), so there
is no way to see TSan output if there is an issue. This can lead to hangs on CI
machines with no accompanying error report to explain the nature of the
hang. For that reason we suggest uninstalling `pytest-xdist` from your
environment to ensure it isn't used. If you need to use `pytest-xdist` to make
the tests complete in a reasonable amount of time, we suggest using
[`pytest-timeout`](https://pypi.org/project/pytest-timeout/) to ensure hung
tests eventually exit, particularly on CI.

TSan includes a check to ensure allocators never fail. This can lead to runtime
crashes if a test happens to try allocating a very large block of memory
specifically to ensure such an allocation does fail correctly. Set
`allocator_may_return_null=1` in `TSAN_OPTIONS` to avoid this.

If a TSan warning is detected, the exit code of the running process will be set
to a nonzero value (66, by default). If for some reason that is problematic in
your test suite then you can set `exitcode=0` in `TSAN_OPTIONS` to make TSan
quit "successfully" if a warning is detected. For example, you might set this if
a subprocess returning a nonzero exit code unexpectedly breaks a test.

You might also find that running your test suite is very slow under
TSan. Consider skipping tests that do not use threads, for example by only
testing files that import `threading` or
`concurrent.futures.ThreadPoolExecutor`. See [this NumPy CI
workflow](https://github.com/numpy/numpy/blob/da268d45aab791023c8d953db6f4597019f770cb/.github/workflows/compiler_sanitizers.yml#L128)
that runs pytest on a subset of NumPy's tests. This will miss tests that spawn
threads in native code (e.g. with OpenMP or other threading primitives) or use
Python packages that spawn threads, but is a good option if your library doesn't
do that.

Altogether, a pytest invocation using TSan might look like:

```
$ TSAN_OPTIONS='allocator_may_return_null=1 halt_on_error=1' pytest -s
```

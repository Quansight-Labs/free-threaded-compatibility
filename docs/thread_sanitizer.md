# Using Thread Sanitizer to validate and test thread safety

## Compiling CPython and foundational packages with ThreadSanitizer

[Thread sanitizer](https://github.com/google/sanitizers/wiki/ThreadSanitizerCppManual) (or TSan) helps
to detect C/C++ data races in concurrent systems. This tool can help to reveal free-threading
related bugs in CPython and foundational packages (e.g. `numpy`).
In this section we provide the commands to build a free-threading compatible
CPython interpreter and packages with ThreadSanitizer and other hints to discover
potential data races.

### `cpython_sanity` docker images

To ease working with thread sanitizer in projects that use Python, NumPy, and
SciPy, we have create a set of docker images that contain a pre-built Python
interpreter and common dependencies that can be tricky to build.

See [the `cpython_sanity`
repository](https://github.com/nascheme/cpython_sanity) for more information
about how to use the docker images. Also see [NumPy PR #28808](https://github.com/numpy/numpy/pull/28808/files),
which adjusted NumPy TSAN CI to use the `ghcr.io/nascheme/numpy-tsan:3.14t-dev`
docker image instead of building Python from source, saving ten minutes of
compute time per CI run.

### Compile free-threaded CPython with ThreadSanitizer

- Clone the latest stable branch (`3.13`):

```bash
git clone https://github.com/python/cpython.git -b 3.13
```

- Configure and build the interpreter. Below instructions are for Linux
    (Windows and macOS may require some changes). We skip the instructions on how
    to install the Clang compiler.

```bash
cd cpython
CC=clang-18 CXX=clang++-18 ./configure --disable-gil --with-thread-sanitizer --prefix $PWD/cpython-tsan
make -j 8
make install
```

- To use the built Python interpreter:

```bash
# Create a virtual environment:
$PWD/cpython-tsan/bin/python3.13t -m venv ~/tsanvenv
# Then activate it:
source ~/tsanvenv/bin/activate

python -VV
# Python 3.13.1 experimental free-threading build (tags/v3.13.1:06714517797, Dec 19 2024, 10:06:54) [Clang 18.1.3 (1ubuntu1)]
PYTHON_GIL=0 python -c "import sys; print(sys._is_gil_enabled())"
# False

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
    this happens for any program compiled with ThreadSanitizer on MacOS and can
    be safely ignored by setting the `MallocNanoZone` environment variable to
    0\. You should only set this in session you are running ThreadSanitizer
    under, as this setting will slow down other programs that allocate memory.

### Compile NumPy with ThreadSanitizer

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
CC=clang-18 CXX=clang++-18 python -m pip install -v . --no-build-isolation -Csetup-args=-Db_sanitize=thread
# or with debug info
# CC=clang-18 CXX=clang++-18 python -m pip install -v . --no-build-isolation -Csetup-args=-Db_sanitize=thread -Csetup-args=-Dbuildtype=debugoptimized
```

## Running Python under ThreadSanitizer

### Useful ThreadSanitizer options

- By default ThreadSanitizer reports warnings. To stop execution on ThreadSanitizer errors, use:

```bash
TSAN_OPTIONS=halt_on_error=1 python -m pytest test.py
```

See [the ThreadSanitizer documentation](https://github.com/google/sanitizers/wiki/ThreadSanitizerFlags) for a full listing of options accepted by ThreadSanitizer.

- To add ThreadSanitizer suppressions (written in a file: `tsan-suppressions`):

```bash
# Let's show an example content of suppressions,
# more info: https://github.com/google/sanitizers/wiki/ThreadSanitizerSuppressions
cat $PWD/tsan-suppressions

race:llvm::RuntimeDyldELF::registerEHFrames
race:partial_vectorcall_fallback
race:dnnl_sgemm


export TSAN_OPTIONS="suppressions=$PWD/tsan-suppressions" python -m pytest test.py
```

### Running pytest tests under ThreadSanitizer

By default, pytest [captures all output from
tests](https://docs.pytest.org/en/stable/how-to/capture-stdout-stderr.html),
this means that you might only see output like `ThreadSanitizer: reported 2 warnings`, but with no accompanying report with details about the warning.

To ensure that pytest doesn't capture any output from ThreadSanitizer, you can
pass `-s` (short for `--show-capture`) to your pytest invocation.

Some authors of this guide have observed hangs running pytest with
`halt_on_error=1`. If you observe hangs, try setting `halt_on_error=0` in
TSAN_OPTIONS.

The [pytest-xdist](https://github.com/pytest-dev/pytest-xdist) plugin can also
sometimes be problematic if a test runner happens to crash during
execution. While `pytest-xdist` does have some support for detecting crashed
worker, it is not foolproof and the authors of this guide have observed hangs on
CI due to pytest-xdist not properly handling a worker failing due to a ThreadSanitizer
error.

The `pytest-xdist` plugin also [makes it impossible to obtain stdout from
a test runner](https://github.com/pytest-dev/pytest-xdist/issues/82), so there
is no way to see ThreadSanitizer output if there is an issue. This can lead to hangs on CI
machines with no accompanying error report to explain the nature of the
hang. For that reason we suggest uninstalling `pytest-xdist` from your
environment to ensure it isn't used. If you need to use `pytest-xdist` to make
the tests complete in a reasonable amount of time, we suggest using
[`pytest-timeout`](https://pypi.org/project/pytest-timeout/) to ensure hung
tests eventually exit, particularly on CI.

ThreadSanitizer includes a check to ensure allocators never fail. This can lead to runtime
crashes if a test happens to try allocating a very large block of memory
specifically to ensure such an allocation does fail correctly. Set
`allocator_may_return_null=1` in `TSAN_OPTIONS` to avoid this.

If a ThreadSanitizer warning is detected, the exit code of the running process will be set
to a nonzero value (66, by default). If for some reason that is problematic in
your test suite then you can set `exitcode=0` in `TSAN_OPTIONS` to make ThreadSanitizer
quit "successfully" if a warning is detected. For example, you might set this if
a subprocess returning a nonzero exit code unexpectedly breaks a test.

You might also find that running your test suite is very slow under
ThreadSanitizer. Consider skipping tests that do not use threads, for example by only
testing files that import `threading` or
`concurrent.futures.ThreadPoolExecutor`. See [this NumPy CI
workflow](https://github.com/numpy/numpy/blob/da268d45aab791023c8d953db6f4597019f770cb/.github/workflows/compiler_sanitizers.yml#L128)
that runs pytest on a subset of NumPy's tests. This will miss tests that spawn
threads in native code (e.g. with OpenMP or other threading primitives) or use
Python packages that spawn threads, but is a good option if your library doesn't
do that.

Altogether, a pytest invocation using ThreadSanitizer might look like:

```
$ TSAN_OPTIONS='allocator_may_return_null=1 halt_on_error=1' pytest -s
```

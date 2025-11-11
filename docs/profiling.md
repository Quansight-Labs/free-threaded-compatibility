# Multithreaded Profiling with samply

Currently, we recommend using [samply](https://github.com/mstange/samply), a
low-level sampling profiler, to identify performance bottlenecks. You can
download binaries from GitHub or build and install locally using a Rust
toolchain. See the samply GitHub page for more details.

While you can also use `perf` or `dtrace` to do similar work, samply provides a
uniform multi-platform interface for this work. You use samply from the
command-line. For example, to record a trace of the execution of a Python
script, you could do:

```bash
samply record python -X perf test.py
```

Note that the `python` here must resolve to a real Python executable.

You can also attach to a running process if you have a PID:

```
samply record --pid $PROCESS_PID
```

Both of these commands instrument the Python interpreter to record the call
stack at regular intervals. Samply then collates this information in a standard
format and opens it in a local version of [the Firefox
profiler](https://profiler.firefox.com).

Once the script is finished - either by exiting or by being interrupted with
Ctrl-C - samply will print out a report and open a web browser pointing at the
profile browser.

Briefly, the interface is broken up into two pieces: a timeline in which
the CPU utilization appears as a graph and a set of panels that allow diving
into the callstack at individual instants in the timeline or aggregated over
selections in the timeline. It's particularly useful to look at the [flame
graph](https://profiler.firefox.com/docs/#/./guide-ui-tour-panels?id=the-flame-graph)
and [stack
chart](https://profiler.firefox.com/docs/#/./guide-ui-tour-panels?id=the-stack-chart)
panels. The former allows identifying calls that are particularly expensive
while the latter allows visualization of how the call stack changes with time.

See [the Firefox profiler documentation](https://profiler.firefox.com/docs/#/) for more details
about how to use the interface.

Note that by default, you will only see information about native
frames. Generally, the call stack will include frames from inside the CPython
interpreter, which will eventually call into a native extension outside the
interpreter, if there is one. If you are analyzing the performance of code that
is pure-Python or goes back and forth between C and Python, you may want to set
up a Linux development environment and follow the instructions below to set up
profiling both native and Python frames in the same profile output.

## Python stack frames on Linux

If you have access to a Linux machine and a Python development environment, then
you can turn on Python's [support for generating perf
events](https://docs.python.org/3/howto/perf_profiling.html) by running Python
with the `-X perf` command-line option:

```bash
samply record python -X perf test.py
```

The resulting profile will include annotations with information about the Python
frames. In the profile browser, Python frames show up in light blue and native
frames show up in yellow.

## Python stack frames on MacOS (Python 3.15+)

MacOS stack frames requires you to use Python 3.15+, which as of this writing you
will need to [compile yourself](installing-cpython.md/#build-from-source). See the documentation of the [dev version of
CPython on how to enable perf events on
MacOX](https://docs.python.org/3.15/howto/perf_profiling.html).

## Uploading profiler data to profiler.firefox.com

The neat thing about using the Firefox profiler as the UI for samply is it means
sharing profiling information over the internet is as easy as clicking a button
in the UI.

By default, samply runs the firefox profiler locally and does not share data it
collects. You can optionally click the upload button in the top-right corner of
the profiler interface to upload the profile data and generate a permalink. This
uploads the data to profiler.firefox.com and others can view the exact same
profiler interface as the one you see locally. This can be a powerful tool to
get help if you don't understand what you are looking at.

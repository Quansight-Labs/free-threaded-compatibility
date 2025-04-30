---
description: py-free-threading is a centralized collection of documentation and trackers around compatibility with free-threaded CPython for the Python open source ecosystem
---

# Python free-threading guide

Free-threaded CPython is coming! :material-language-python: :thread:

## Status

After the [acceptance by the Python Steering Council](https://discuss.python.org/t/a-steering-council-notice-about-pep-703-making-the-global-interpreter-lock-optional-in-cpython/30474) of
[PEP 703 - Making the Global Interpreter Lock Optional in CPython](https://peps.python.org/pep-0703/), work is happening for the [gradual rollout strategy](https://discuss.python.org/t/pep-703-making-the-global-interpreter-lock-optional-in-cpython-acceptance/37075) in CPython.
In parallel, efforts to support free-threading are underway across the Python ecosystem, including packages, third-party libraries, tooling, and education.

## Purpose of this site

This website serves as a **centralized resource** for Python package
maintainers, as well as end users, interested in supporting or experimenting with
free-threaded Python.

It also tracks the **compatibility status of packages**
that include native code here:

- [Free-threading Python Compatibility Status Tracker](tracking.md)

It offers **documentation and guidance** for setting up a
free-threaded Python development environment and getting code working under the
free-threaded build.

## Install free-threaded Python

The following sections describe how to install free-threaded Python, run it, and verify
the GIL is disabled.

- [Installing Free-Threaded Python](installing-cpython.md)
- [Running Python with the GIL Disabled](running-gil-disabled.md)

## Run your code on free-threaded Python

If you are interested in updating your code to work on free-threaded Python,
your next steps depend on your needs and goals. To begin, select the option
that best describes you:

??? success "I am writing a Python script or application that uses Python libraries I don't maintain"

    You should start experimenting with free-threaded Python once the libraries
    you depend on advertise support for free-threading. See [the tracking
    table](tracking.md) for more details about the status of free-threaded
    support in Python libraries.

    If your dependencies advertise free-threaded support, good news! If you do
    not use the `threading` module and do not plan to, then you're done and you
    can feel safe declaring support for running your project on the
    free-threaded build.

    If you would like to use the `threading` module to improve the performance of
    your project, you should read the documentation of your dependencies and
    learn about their thread safety guarantees. This is particularly true of
    libraries that expose mutable objects, doubly so if you want to mutate a
    shared object from many threads.

    Pure Python code can exhibit thread safety issues, so you may also want to
    look at the first section of the porting guide, particularly on the thread
    safety of pure Python code:

    - [Porting Python Packages to Support Free-Threading](porting.md)

??? success "I maintain a pure Python app or tool written in pure Python with no public Python API"

    You should start experimenting with free-threaded Python once the libraries
    you depend on advertise support for free-threading. See [the tracking
    table](tracking.md) for more details about the status of free-threaded
    support in Python libraries.

    If your dependencies advertise free-threaded support, good news! If you do
    not use the `threading` module and do not plan to, then you're done and you
    can feel safe declaring support for running your project on the
    free-threaded build.

    If you make use of the `threading` module internally and already have
    multithreaded tests, consider experimenting with your existing tests with a
    very short [thread switch
    interval](https://docs.python.org/3/library/sys.html#sys.getswitchinterval). This
    can elicit thread safety issues on the GIL-enabled build. If you do not use
    `threading` or thread pools internally your tool or app should behave
    identically under free-threading.

    If you would like to use the `threading` module to improve the performance of
    your project, you should read the documentation of your dependencies and
    learn about their thread safety guarantees. This is particularly true of
    libraries that expose mutable objects, doubly so if you want to mutate a
    shared object from many threads.

    Pure Python code can exhibit thread safety issues, so you may also want to
    look at the first section of the porting guide, particularly on the thread
    safety of pure Python code:

    - [Porting Python Packages to Support Free-Threading](porting.md)

??? success "I maintain a pure Python package with a public Python API"

    Free-threading is implemented in CPython such that pure Python code is
    thread-safe, at least to the same extent as it is with the GIL enabled
    today. We use "thread-safe" here to mean that CPython should not crash
    running multithreaded pure Python code, not necessarily that a multithreaded
    program will always produce deterministic results, even if the GIL-enabled
    build is deterministic. It is up to the author of a program, application, or
    library to ensure safe multithreaded usage when using the library in a
    supported manner.

    There are a few ways you can create thread safety issues in your own
    code. The most common ones are: using global state for configuration or
    other purposes, implementing a cache with a dict or other variable not meant
    for that purpose, or using functionality of a dependency that itself isn't
    thread-safe. You should also think about whether you would like to support
    multithreaded use of any mutable data structures exposed by your package. If
    your package does none of those things, you are very likely ready for
    free-threading already.

    What gets trickier is testing whether your package is thread-safe. For that
    you'll need multi-threaded tests, and that can be more involved - see [our guide
    to adding multithreaded test coverage](testing.md) to Python packages.

    - [Porting Python Packages to Support Free-Threading](porting.md)
    - [Improving Multithreaded Test Coverage](testing.md)

??? success "I maintain a Python package with compiled extension modules"

    As usual with extensions, dealing with native code will take some work but
    we hope that this guide will provide you with a toolkit to get things
    working.

    We suggest reading through the the full porting guide, including the final
    section that focuses on considerations for native code.

    - [Porting Python Packages to Support Free-Threading](porting.md)
    - [Improving Multithreaded Test Coverage](testing.md)
    - [Updating Native Extensions to Support Free-Threading](porting-extensions.md)

## Frequently asked questions about errors

- [Frequently seen errors and how to fix them](faq.md)

## Advanced topics for package maintainers

- [Setting up Continuous Integration](ci.md)
- [Debugging Thread Safety Issues](debugging.md)

## Further reading

We've collected additional resources on free-threaded Python and multithreaded
programming here:

- [More Resources](resources.md)

## News and getting help

You can join the Free-threaded Python Community Discord using this invite link:
[https://discord.gg/rqgHCDqdRr](https://discord.gg/rqgHCDqdRr).

You can also ask questions in the [Threading
category](https://discuss.python.org/c/threading/38) of the Python community
Discourse forum.

Please read and be mindful of community rules. Both communities enforce the
Python Software Foundation Code of Conduct.

## Contributing

We welcome your contributions.
Please read the
[Contributing](contributing.md) page for more details.
Please open issues or pull requests
[on this repo](https://github.com/Quansight-Labs/free-threaded-compatibility)
for anything that seems in scope for this site or for tracking issues related
to support for free-threaded Python across the ecosystem.

## About this site

This site is maintained primarily by Quansight Labs, where a team is working
together with the Python runtime team at Meta and stakeholders across the
ecosystem to jumpstart work on converting the libraries that make up the
scientific Python and AI/ML stacks to work with the free-threaded build of
CPython 3.13. Additionally, that effort will look at libraries like PyO3 that
are needed to interface with CPython from other languages.

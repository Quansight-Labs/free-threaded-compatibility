## Improving Ecosystem Compatibility with Free-Threaded Python

Quansight Labs is working with stakeholders across the ecosystem to
jumpstart work on converting the libraries that make up the scientific
python and AI/ML stacks to work with the free-threaded (nogil)
build of CPython 3.13. Additionally, we will look at libraries like `PyO3`
that are needed to interface with CPython from other languages.

Our initial goal is to ensure libraries at the bottom of the stack like
NumPy, pybind11, and cython are runnable. We will also be updating
packaging tools like meson-python needed to support building wheels for
free-threaded CPython. Once those are runnable, we will begin looking at
libraries higher in the stack.

### What is this repository?

This repository is for coordinating ecosystem-wide work. We will use
this repository to track, understand, and provide documentation for
dealing with issues that we find are common across many
libraries. Issues that are specific to a project should be reported in
that project's issue tracker.

### Building Free-Threaded CPython

Currently we suggest building CPython from source using the latest
version of the CPython `main` branch. See [the build
instructions](https://devguide.python.org/getting-started/setup-building/index.html)
in the CPython developer guide. You will need to install [needed
third-party
dependencies](https://devguide.python.org/getting-started/setup-building/index.html#install-dependencies)
before building. To build the free-threaded version of CPython, pass
`--disable-gil` to the `configure` script:

```bash
./configure --with-pydebug --disable-gil
```

If you will be switching Python versions often, it may make sense to
build CPython using [pyenv](https://github.com/pyenv/pyenv). We suggest
installing the
[pyenv-suffix](https://github.com/AdrianDAlessandro/pyenv-suffix) plugin
to distinguish between free-threaded and "standard" builds of CPython
3.13:

```bash
CONFIGURE_OPTS="--disable-gil --with-pydebug"
PYENV_VERSION_SUFFIX='-nogil' pyenv install -v 3.13-dev
```

You can then "activate" the installed free-threaded python in your
global shell environment with

```bash
pyenv global 3.13-dev-nogil
```

Or locally in a single directory with a `.python-version` file or with

```bash
pyenv local 3.13-dev-nogil
```

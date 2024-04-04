We suggest installing the
[pyenv-suffix](https://github.com/AdrianDAlessandro/pyenv-suffix) plugin to
distinguish between free-threaded and "standard" builds of CPython 3.13:

```bash
CONFIGURE_OPTS="--disable-gil" PYENV_VERSION_SUFFIX='-nogil' \
pyenv install -v --debug 3.13-dev
```

You can then "activate" the installed free-threaded python in your
global shell environment with

```bash
pyenv global 3.13-dev-nogil-debug
```

Or locally in a single directory with a `.python-version` file or with

```bash
pyenv local 3.13-dev-nogil-debug
```

To install the `nogil-integration` branch, clone this repository and
install using the provided definition file in this folder:

```bash
CONFIGURE_OPTS="--disable-gil" PYENV_VERSION_SUFFIX='-nogil-integration' \
pyenv install -v --debug /path/to/free-threaded-compatibility/pyenv/3.13-dev
```

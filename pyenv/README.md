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

Note that debug builds of python are substantially slower. You can drop
`--debug` from the `pyenv install` invocation if you would like an optimized 
build. The resulting pyenv environments will not have a `-debug` suffix in 
their names.

You can simultaneously install the build of python with the GIL enabled with

```bash
pyenv install -v --debug 3.13-dev
```

The resulting environment can be activated with

```bash
pyenv global 3.13-dev
```

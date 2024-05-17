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

If you need to install a CPython development tree, either locally or on GitHub,
you can do so using a [custom
definition](https://github.com/pyenv/pyenv/blob/master/plugins/python-build/README.md#custom-definitions),
e.g. based on the definition for
[3.13-dev](https://github.com/pyenv/pyenv/blob/master/plugins/python-build/share/python-build/3.13-dev). Replace
the repository used in that definition with a CPython fork or local clone and
replace `3.13` with the branch you would like to build. The commit you would
like to build must have a branch pointing to it. If your custom definition
should have the same name as the original definition, but with edited paths and
branch names. Install it with e.g. this command:

```bash
CONFIGURE_OPTS=--disable-gil PYENV_VERSION_SUFFIX='-nogil-branch' pyenv install -v ./3.13-dev
```

And it will be available to activate via the `pyenv` CLI with the name
`3.13-dev-nogil-branch`.

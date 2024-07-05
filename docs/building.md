## Building Free-Threaded CPython

Currently we suggest building CPython from source using the latest version of
the CPython `main` branch. See [the
build
instructions](https://devguide.python.org/getting-started/setup-building/index.html)
in the CPython developer guide. You will need to install [needed third-party
dependencies](https://devguide.python.org/getting-started/setup-building/index.html#install-dependencies)
before building. To build the free-threaded version of CPython, pass
`--disable-gil` to the `configure` script:

```bash
./configure --with-pydebug --disable-gil
```

If you will be switching Python versions often, it may make sense to
build CPython using [pyenv](https://github.com/pyenv/pyenv). In order to
do that, you can use the following:

```bash
pyenv install --debug 3.13t-dev
```

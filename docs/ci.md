# Setting up CI

While you may extend the following instructions to also set up CI on 3.13t, we
recommend focusing on 3.14+.

## CI setup via `setup-python`

The easiest way to get a free-threaded Python build on a CI runner is with the
[`setup-python`](https://github.com/actions/setup-python) Github Action:

```yaml
jobs:
  free-threaded:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@...
      - uses: actions/setup-python@...
        with:
          python-version: 3.14t
```

## CI setup via `setup-uv`

An alternative to `setup-python` is to use
[`setup-uv`](https://github.com/astral-sh/setup-uv) Github Action:

```yaml
jobs:
  free-threaded:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@...
      - uses: astral-sh/setup-uv@...
        with:
          python-version: 3.14t
```

You should replace the ellipses with versions for the actions.

## Windows CI setup via custom PowerShell

For installing a free-threaded build of Python on a Windows CI runner
(`runs-on: windows-latest`), you can download and install directly from
[https://www.python.org/ftp/python/](https://www.python.org/ftp/python/) as
shown in the following PowerShell snippet (noting that the free-threaded
binary is named `python{version}t.exe`, where the "t" is for free-"t"hreaded).
For more tips see the [docs on silent installation and options on
Windows](https://docs.python.org/3/using/windows.html#installing-without-ui).

```yaml
jobs:
  free-threaded:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@...
      - name: custom python install script
        shell: pwsh
        run: |
          $pythonInstallerUrl = 'https://www.nuget.org/api/v2/package/python-freethreaded/3.13.1'
          Invoke-WebRequest $pythonInstallerUrl -OutFile 'python-freethreaded.3.13.1.nupkg'
          Install-Package python-freethreaded -Scope CurrentUser -Source $pwd
          $python_dir = (Get-Item((Get-Package -Name python-freethreaded).Source)).DirectoryName
          $env:path = $python_dir + "\tools;" + $python_dir + "\tools\Scripts;" + $env:Path
```

## Building free-threaded wheels with cibuildwheel

[cibuildwheel](https://cibuildwheel.pypa.io/en/stable/) 3.1+ has support for
building free-threaded wheels on all platforms and will build free-threaded
wheels for Python 3.14 and newer in its default configuration. If your project
releases nightly wheels, we suggest configuring `cibuildwheel` to build nightly
free-threaded wheels.

As of April 2026, we suggest not enabling builds for Free-threaded Python 3.13 going
forward. The 3.13t release was considered experimental, is approximately 30%
slower in single-threaded performance than 3.14t, and does not include a number
of safety fixes for builtins and the standard library that were included in
3.14t. Free-threaded 3.14 also has better ecosystem compatibility than 3.13.

You will also likely need to manually pass `-Xgil=0` or set `PYTHON_GIL=0` in
your shell environment while running tests to ensure the GIL is actually
disabled during tests, at least until you can register that your extension
modules support disabling the GIL via
[`Py_mod_gil`](https://docs.python.org/3/c-api/module.html#c.Py_mod_gil) and all
of your runtime test dependencies do the same. See [the porting
guide](porting.md) for more information about declaring support for
free-threaded Python in your extension.

!!! info

    If a dependency of your package does not support free-threading or has not
    yet done a release which includes `cp314t` wheels, this can be tricky to
    work around because an environment marker for free-threading does not exist
    (see [this Discourse thread](https://discuss.python.org/t/environment-marker-for-free-threading/60007)).
    Hence it is not possible to special-case free-threading with static metadata
    in `pyproject.toml`. It's fine to still upload `cp314t` wheels for your
    package to PyPI; the user may then be responsible for getting the
    dependency installed (e.g., from a nightly wheel or building the
    dependency's `main` branch from source) if the last release of the
    dependency doesn't cleanly build from source or doesn't work under
    free-threading.

## CI Timeouts

With free-threading, deadlocks and hangs are more likely.
GitHub Actions and other Continuous Integration systems often support timeouts:
[timeout-minutes](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax#jobsjob_idtimeout-minutes)

```
jobs:
  test_freethreading:
    timeout-minutes: 10
    steps:
      - uses: actions/checkout@...
      ...
```

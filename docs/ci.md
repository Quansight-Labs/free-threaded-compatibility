# Setting up CI

Currently the `setup-python` GitHub Action [does not
support](https://github.com/actions/setup-python/issues/771) installing a
free-threaded build. For now, here are some relatively easy ways:

## Ubuntu Linux CI setup via `deadsnakes-action`

The easiest way to get a free-threaded Python build on a CI runner is with the
`deadsnakes` Ubuntu PPA and the `deadsnakes-action` GitHub Action:

```yaml
jobs:
  free-threaded:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@...
      - uses: deadsnakes/action@...
        with:
          python-version: 3.13-dev
          nogil: true
```

You should replace the ellipses with versions for the actions. If there is a
newer CPython 3.13 release available since this document was written or
updated, use that version instead.

## Windows CI setup via custom PowerShell

For installing a free-threaded build of Python on a Windows CI runner
(`runs-on: windows-latest`), you can download and install directly from
[https://www.python.org/ftp/python/](https://www.python.org/ftp/python/) as
shown in the following PowerShell snippet (noting that the free-threaded
binary is named `python{version}t.exe`, where the "t" is for free-"t"hreaded).
For more tips see the [docs on silent installation and options on
Windows](https://docs.python.org/3.13/using/windows.html#installing-without-ui).

```yaml
jobs:
  free-threaded:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@...
      - name: custom python install script
        shell: pwsh
        run: |
          $pythonInstallerUrl = "https://www.python.org/ftp/python/3.13.0/python-3.13.0rc2-amd64.exe"
          Invoke-WebRequest $pythonInstallerUrl -OutFile setup-python.exe
          Start-Process "setup-python.exe" -argumentlist "/quiet PrependPath=1 TargetDir=C:\Python313 Include_freethreaded=1" -wait
          C:\Python313\python3.13t.exe -m pip install -r requirements.txt
          C:\Python313\python3.13t.exe -c "import sys; print(sys._is_gil_enabled())"
```

## Building free-threaded wheels with cibuildwheel

[cibuildwheel](https://cibuildwheel.pypa.io/en/stable/) has support
for building free-threaded wheels on all platforms. If your project releases
nightly wheels, we suggest configuring `cibuildwheel` to build nightly
free-threaded wheels.

If your project depends on Cython or the NumPy C API, you will need to install a
Cython and/or NumPy nightly wheel in the build, as the newest stable release of
Cython cannot generate code that will compile under the free-threaded build and
the newest stable release of NumPy does not support free-threaded python. Cython
3.1.0 and NumPy 2.1.0 will be the first stable releases to support free-threaded
python.

You can install nightly wheels for both Cython and NumPy using the following
install command:

```bash
pip install -i https://pypi.anaconda.org/scientific-python-nightly-wheels/simple cython numpy
```

To ensure wheels are built correctly under cibuildwheel, you will need to
specify the following variables in the environment for the cibuildwheel action:

```yaml
  - name: Build wheels
    uses: pypa/cibuildwheel@...
    env:
      CIBW_PRERELEASE_PYTHONS: true
      CIBW_FREE_THREADED_SUPPORT: true
      CIBW_BUILD: cp313t-${{ matrix.buildplat }}
      # TODO:
      # remove when a released cython can build free-threaded extensions
      CIBW_BUILD_FRONTEND: 'pip; args: --no-build-isolation'
```

As above, replace the ellipses with a `cibuildwheel` version.

If for some reason disabling build isolation is unworkable, you can also tell
pip about the nightly wheel index and it will use it in an isolated build. To
do this, set:

```yaml
CIBW_BUILD_FRONTEND: 'pip; args: --pre --extra-index-url "https://pypi.anaconda.org/scientific-python-nightly-wheels/simple"'
```

Many projects use `build` instead of `pip` for the build frontend. See [the
cibuildwheel](https://cibuildwheel.pypa.io/en/stable/options/#build-frontend)
docs for more information about how to pass arguments to `build` and `pip`. See
[this
comment](https://github.com/pypa/build/issues/651#issuecomment-2243025713) on
the `build` issue tracker if you need to use `build` and cannot disable build
isolation.

Note that nightly wheels may not be available on all platforms yet. Windows
wheels, in particular, are not currently available for NumPy or projects that
depend on NumPy (e.g., SciPy).

You will also likely need to manually pass `-Xgil=0` or set `PYTHON_GIL=0` in
your shell environment while running tests to ensure the GIL is actually
disabled during tests, at least until you can register that your extension
modules support disabling the GIL via `Py_mod_gil` and all of your runtime test
dependencies do the same. See [the porting guide](porting.md) for more
information about declaring support for free-threaded python in your extension.

# Setting up CI

Currently the `setup-python` GitHub Action [does not
support](https://github.com/actions/setup-python/issues/771) installing a
free-threaded build. For now, the easiest way to get a free-threaded Python
build on a CI runner is with the `deadsnakes` Ubuntu PPA and the
`deadsnakes-action` GitHub Action:

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

[cibuildwheel](https://cibuildwheel.pypa.io/en/stable/) has support
for building free-threaded wheels on all platforms. If your project releases
nightly wheels, we suggest configuring `cibuildwheel` to build nightly
free-threaded wheels.

You will need to specify the following variables in the environment for the
cibuildwheel action:

```yaml
  - name: Build wheels
    uses: pypa/cibuildwheel@...
    env:
      CIBW_PRERELEASE_PYTHONS: true
      CIBW_FREE_THREADED_SUPPORT: true
      CIBW_BUILD: cp313t-${{ matrix.buildplat }}
          # TODO: remove along with installing build deps in
          # cibw_before_build.sh when a released cython can build numpy
      CIBW_BUILD_FRONTEND: 'pip; args: --no-build-isolation'
```

As above, replace the ellipses with a `cibuildwheel` version.

If your project depends on Cython, you will need to install a Cython nightly
wheel in the build, as the newest stable release of Cython cannot generate code
that will compile under the free-threaded build. You likely do not need to
disable `pip`'s build isolation if your project does not depend on Cython.

You can install nightly wheels for Cython and NumPy using the following
install command:

```bash
pip install -i https://pypi.anaconda.org/scientific-python-nightly-wheels/simple cython numpy
```

Note that nightly wheels may not be available on all platforms yet. Windows
wheels, in particular, are not currently available for NumPy or projects that
depend on NumPy (e.g., SciPy).

You will also likely need to manually pass `-Xgil=0` or set `PYTHON_GIL=0` in
your shell environment while running tests to ensure the GIL is actually
disabled during tests, at least until you can register that your extension
modules support disabling the GIL via `Py_mod_gil` and all of your runtime test
dependencies do the same. It is not currently possible to mark that a Cython
module supports running without the GIL.

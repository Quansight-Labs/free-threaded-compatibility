---
ref: abi3t
---

# Building and distributing `abi3t` extensions

Starting with CPython 3.15, native extensions can target the [free-threaded
Stable ABI, `abi3t`](https://docs.python.org/3.15/howto/abi3t-migration.html).
On each platform, one wheel tagged `cp315-abi3.abi3t` can run on both the
GIL-enabled and free-threaded builds of CPython 3.15 and later.

Publishing an `abi3t` wheel is optional; it is not required to support
free-threaded Python. The ABI also does not make an extension safe to use
without the GIL. First [port and test the extension for
free-threading](porting-extensions.md), then decide whether publishing fewer
wheels is worth the restrictions of the Stable ABI.

## Supporting older Python versions

`abi3t` wheels support only Python 3.15 and newer. For a project supporting
Python 3.11 and later, we suggest publishing these three wheels on each
platform:

| Wheel tag          | Compatible CPython builds                    |
| ------------------ | -------------------------------------------- |
| `cp311-abi3`       | GIL-enabled 3.11 and later                   |
| `cp314-cp314t`     | Free-threaded 3.14 only                      |
| `cp315-abi3.abi3t` | GIL-enabled and free-threaded 3.15 and later |

Build the ordinary `abi3` wheel with the oldest Python version your project
supports. The examples below use Python 3.11.

Free-threaded 3.14 predates `abi3t`, so it still needs a version-specific
`cp314-cp314t` wheel.

## Build tools

Build-tool support varies:

| Build path                   | Status                                                                                                                                                                                           |
| ---------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| CMake with scikit-build-core | Released in [CMake 4.4](https://cmake.org/cmake/help/latest/release/4.4.html) and [scikit-build-core 1.0](https://scikit-build-core.readthedocs.io/en/stable/about/changelog.html#version-1-0-0) |
| Maturin with PyO3            | Initial support in [Maturin 1.14.0](https://github.com/PyO3/maturin/releases/tag/v1.14.0); use [1.14.1+](https://github.com/PyO3/maturin/releases/tag/v1.14.1) with both ABI families            |
| meson-python                 | Released in [meson-python 0.21.0](https://mesonbuild.com/meson-python/changelog.html); `abi3t` builds need a free-threaded interpreter                                                           |
| setuptools                   | [Under development](https://github.com/pypa/setuptools/pull/5193)                                                                                                                                |

=== "CMake with scikit-build-core"

    CMake 4.4 supports `abi3t`, and scikit-build-core 1.0+ generates the
    corresponding wheel tag. To build the three wheels listed above, use
    `cp311` for GIL-enabled interpreters and an
    [override](https://scikit-build-core.readthedocs.io/en/stable/configuration/overrides.html)
    for free-threaded Python 3.15 and newer. Add the following to your existing
    `pyproject.toml`:

    ```toml
    [build-system]
    requires = ["scikit-build-core>=1.0"]
    build-backend = "scikit_build_core.build"

    [tool.scikit-build]
    wheel.py-api = "cp311"

    [[tool.scikit-build.overrides]]
    if.abi-flags = "t"
    if.python-version = ">=3.15"
    wheel.py-api = "cp315.cp315t"
    ```

    A minimal `CMakeLists.txt` fragment looks like this:

    ```cmake
    cmake_minimum_required(VERSION 4.4)
    project(example LANGUAGES C)

    find_package(
      Python 3.11 REQUIRED COMPONENTS
      Interpreter Development.Module ${SKBUILD_SABI_COMPONENT})
    if(SKBUILD_SABI_VERSION)
      Python_add_library(
        _core MODULE src/_core.c USE_SABI ${SKBUILD_SABI_VERSION} WITH_SOABI)
    else()
      Python_add_library(_core MODULE src/_core.c WITH_SOABI)
    endif()
    install(TARGETS _core DESTINATION example)
    ```

    Build separately with GIL-enabled Python 3.11, free-threaded Python 3.14,
    and free-threaded Python 3.15 to produce `cp311-abi3`, `cp314-cp314t`, and
    `cp315-abi3.abi3t`, respectively. Scikit-build-core leaves
    `SKBUILD_SABI_VERSION` empty on free-threaded Python 3.14, which has no
    Stable ABI. On the other builds, it selects 3.11 or 3.15 to match the
    wheel tag. The extension source must support each selected API.

    Setting `wheel.py-api = "cp315.cp315t"` unconditionally targets Python
    3.15 and later; it does not also produce an `abi3` wheel for Python 3.11.

    See the complete [scikit-build-core `abi3t`
    example](https://scikit-build-core.readthedocs.io/en/stable/guide/getting_started.html)
    and CMake's [`FindPython`
    reference](https://cmake.org/cmake/help/v4.4/module/FindPython.html#commands).
    The scikit-build-core example also includes a fallback for CMake versions
    older than 4.4.

=== "meson-python"

    [meson-python 0.21.0](https://mesonbuild.com/meson-python/changelog.html)
    added `abi3t` support. Its [Limited API build
    guide](https://mesonbuild.com/meson-python/how-to-guides/limited-api.html)
    recommends making Stable ABI builds opt-in. Add the following to your
    existing `pyproject.toml`:

    ```toml
    [build-system]
    requires = ["meson-python>=0.21.0", "meson>=1.7.0"]
    build-backend = "mesonpy"

    [tool.meson-python]
    limited-api = true
    ```

    In `meson.build`, select the API version as described in the
    [`abi3t` instructions](https://mesonbuild.com/meson-python/how-to-guides/limited-api.html#the-abi3t-stable-abi):

    ```meson
    project(
      'example', 'c',
      meson_version: '>=1.7.0',
      default_options: ['python.allow_limited_api=false'],
    )

    py = import('python').find_installation(pure: false)
    api_version = '3.11'
    if py.language_version().version_compare('>=3.15')
      if py.get_variable('Py_GIL_DISABLED') == 1
        api_version = '3.15'
      endif
    endif

    py.extension_module(
      '_core', 'src/_core.c',
      limited_api: api_version,
      subdir: 'example',
      install: true,
    )
    ```

    Enable the Limited API for the two Stable ABI builds; leave it disabled
    for free-threaded Python 3.14:

    ```bash
    python3.11 -m build --wheel -Csetup-args=-Dpython.allow_limited_api=true
    python3.14t -m build --wheel
    python3.15t -m build --wheel -Csetup-args=-Dpython.allow_limited_api=true
    ```

    These commands produce `cp311-abi3`, `cp314-cp314t`, and
    `cp315-abi3.abi3t` wheels, respectively. Meson-python takes the wheel's
    Python version tag from the build interpreter, regardless of
    `limited_api`, so build the first wheel with Python 3.11. Building for
    `abi3t` currently requires a free-threaded interpreter.

=== "setuptools"

    **No released version supports `abi3t` yet.** Released versions reject
    `py_limited_api` on free-threaded builds. Follow [setuptools pull request
    5193](https://github.com/pypa/setuptools/pull/5193) and the [tracking
    issue](https://github.com/pypa/setuptools/issues/5205) for the proposed
    support.

    Until that work is released, use version-specific free-threaded wheels. The
    [setuptools extension module
    documentation](https://setuptools.pypa.io/en/latest/userguide/ext_modules.html)
    remains the reference for its general C/C++ build configuration.

## Extension APIs, bindings, and code generators

The extension API, language binding, or source generator you use must support
`abi3t`. The build backend must also assign the correct extension and wheel
tags. Check both layers before publishing.

### CPython C API

For extensions written directly against the CPython C API, follow CPython's
[`abi3t` migration
HOWTO](https://docs.python.org/3.15/howto/abi3t-migration.html). The ordinary
Limited API documentation does not cover the `abi3t`-specific changes. The
HOWTO explains the new module initialization convention and the major C API
restrictions.

If your build tool does not define the target selector, define it before
including `Python.h`:

```c
#define Py_TARGET_ABI3T 0x030f0000
#include <Python.h>
```

The selector controls only the API available at compile time. On platforms
that use `.so` extensions, the built extension must also have an `.abi3t.so`
suffix. Python 3.15 permits [Stable ABI filenames with a multiarch
tuple](https://docs.python.org/3.15/whatsnew/3.15.html#other-language-changes),
such as `.abi3t-x86_64-linux-gnu.so`. Windows keeps the `.pyd` suffix. You must
also give the wheel the correct tag, so prefer a build backend with native
support. See the [Stable ABI
reference](https://docs.python.org/3.15/c-api/stable.html) for the precise
contract.

### PyO3 and Maturin

[PyO3 0.29+](https://pyo3.rs/latest/features.html#abi3t) and [Maturin
1.14.0+](https://www.maturin.rs/bindings) support `abi3t`. Use Maturin 1.14.1 or
newer when enabling both Stable ABI families:

```toml
pyo3 = { version = "0.29", features = ["abi3-py311", "abi3t-py315"] }
```

Build each family with the corresponding interpreter:

```bash
maturin build --interpreter python3.11
maturin build --interpreter python3.15t
```

Each `maturin build` command selects one ABI family. See the [PyO3 build and
distribution guide](https://pyo3.rs/latest/building-and-distribution.html) for
the complete workflow. Free-threaded 3.14 still needs its own version-specific
wheel.

### CFFI

[CFFI 2.1.1+](https://cffi.readthedocs.io/en/stable/whatsnew.html#v2-1-1) can
generate extension sources that target `abi3t` when compiled for CPython 3.15.
The upstream [`cffi-gen-src`
documentation](https://cffi.readthedocs.io/en/stable/cffi-gen-src.html)
already provides complete Meson and setuptools integration examples, so use
those instead of duplicating their source-generation setup here.

CFFI does not assign the final wheel tag by itself. Pair it with an
`abi3t`-capable backend, such as the CMake with scikit-build-core or
meson-python paths above. The upstream Meson example does not target the
Stable ABI; add the `limited_api` argument and the `limited-api` setting from
the meson-python tab. Until setuptools support is released, CFFI projects using
setuptools should publish version-specific free-threaded wheels.

### Cython

Cython does not yet provide released `abi3t` support. You can experiment with
the upstream
[`freethreading-limited-api-preview`](https://github.com/cython/cython/tree/freethreading-limited-api-preview)
branch, but expect bugs and unsupported Cython features.

### nanobind

Current nanobind releases support version-specific free-threaded extensions
and ordinary `abi3`, but not `abi3t`. The [split-mode
documentation](https://nanobind.readthedocs.io/en/latest/split_mode.html)
describes a preview implementation with an `abi3t` frontend.

## Verify and test the wheel

Before publishing an `abi3t` wheel:

1. Configure the build to target `abi3t`. Some backends, including CMake with
    scikit-build-core and meson-python, require building with a free-threaded
    CPython 3.15 interpreter; others can target it from a GIL-enabled build.
1. If you target Python 3.15, confirm that the wheel name contains
    `cp315-abi3.abi3t` and, on Unix-like systems, that the extension filename
    uses an `abi3t` suffix such as `.abi3t.so` or
    `.abi3t-<multiarch>.so`. Windows extension filenames continue to end in
    `.pyd`.
1. Test the wheel with both GIL-enabled and free-threaded builds of every
    supported Python version, following CPython's [`abi3t` testing
    guidance](https://docs.python.org/3.15/howto/abi3t-migration.html#testing).
    The worked example below shows how to cross-test one wheel. For general CI
    setup and testing strategies, see [Setting up CI](ci.md) and [Validating
    thread safety with testing](testing.md).
1. Document the minimum supported installer version. [pip 26.1 or
    newer](https://pip.pypa.io/en/stable/news/#v26-1) recognizes the combined
    tag.

### Worked GitHub Actions cross-test

Use [cibuildwheel](ci.md#building-free-threaded-wheels-with-cibuildwheel) to
build and test with free-threaded Python, then pass the wheel to a separate
job that tests with GIL-enabled Python. This example covers Linux, macOS, and
Windows, with one wheel per platform.

The project must already be configured to produce `abi3t` wheels. For the
opt-in meson-python example above, uncomment `CIBW_CONFIG_SETTINGS` below.
Replace `pytest` and `tests` with your project's test dependencies and test
suite as needed.

The workflow disables cibuildwheel's default `abi3audit` check because
[`abi3t` auditing is not yet supported](https://github.com/pypa/abi3audit/issues/215).
Released `abi3audit` rejects the `PyModExport_*` entry point required by
`abi3t`. Wheel repair and the tests on both interpreter builds still run.

```yaml
name: abi3t cross-test

on:
  pull_request:
  push:

jobs:
  build:
    runs-on: ${{ matrix.os }}
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-latest, macos-15, windows-latest]
    steps:
      - uses: actions/checkout@v7
      - uses: pypa/cibuildwheel@v4.2.1
        env:
          CIBW_BUILD: cp315t-*
          CIBW_SKIP: '*-musllinux_*'
          CIBW_ARCHS: auto64
          CIBW_AUDIT_COMMAND: ''
          CIBW_TEST_REQUIRES: pytest
          CIBW_TEST_COMMAND: python -m pytest {project}/tests
          # For the opt-in meson-python configuration above:
          # CIBW_CONFIG_SETTINGS: setup-args=-Dpython.allow_limited_api=true
      - uses: actions/upload-artifact@v7
        with:
          name: abi3t-${{ matrix.os }}
          path: wheelhouse/*.whl

  test-gil:
    needs: build
    runs-on: ${{ matrix.os }}
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-latest, macos-15, windows-latest]
    steps:
      - uses: actions/checkout@v7
      - uses: actions/setup-python@v7
        with:
          python-version: '3.15'
          allow-prereleases: true
      - uses: actions/download-artifact@v8
        with:
          name: abi3t-${{ matrix.os }}
          path: wheelhouse
      - name: Install and test the same wheel
        shell: bash
        run: |
          python -m pip install --upgrade 'pip>=26.1'
          python -m pip install wheelhouse/*.whl pytest
          python -Im pytest tests
```

Cibuildwheel tests the installed wheel in a separate environment using the
free-threaded interpreter selected by `CIBW_BUILD`. The second job downloads
that wheel and tests it with GIL-enabled Python 3.15. On Linux, cibuildwheel
builds manylinux wheels; musllinux wheels are excluded because the second job
runs on Ubuntu. In production, pin third-party actions to commit SHAs.

Python 3.15 is the first release with `abi3t`. Add GIL-enabled and free-threaded
tests for every later Python version you support.

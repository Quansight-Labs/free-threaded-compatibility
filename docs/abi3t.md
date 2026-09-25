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

| Build path                   | Status                                                                                                                                                                                   |
| ---------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| CMake with scikit-build-core | Released in [CMake 4.4](https://cmake.org/cmake/help/latest/release/4.4.html) and [scikit-build-core 1.0](https://scikit-build.readthedocs.io/en/latest/history.html#scikit-build-1-0-0) |
| Maturin with PyO3            | Initial support in [Maturin 1.14.0](https://github.com/PyO3/maturin/releases/tag/v1.14.0); use [1.14.1+](https://github.com/PyO3/maturin/releases/tag/v1.14.1) with both ABI families    |
| meson-python                 | [Implemented upstream](https://github.com/mesonbuild/meson-python/pull/856) but not released                                                                                             |
| setuptools                   | [Under development](https://github.com/pypa/setuptools/pull/5193)                                                                                                                        |

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
    wheel.py-api = "cp315.cp315t"
    ```

    A minimal `CMakeLists.txt` fragment looks like this:

    ```cmake
    cmake_minimum_required(VERSION 4.4)
    project(example LANGUAGES C)

    find_package(
      Python 3.15 REQUIRED COMPONENTS Interpreter Development.SABIModule)
    Python_add_library(
      _core MODULE src/_core.c USE_SABI 3.15 WITH_SOABI)
    install(TARGETS _core DESTINATION example)
    ```

    Build with a free-threaded Python 3.15 interpreter to produce the combined
    `cp315-abi3.abi3t` wheel. A build with a GIL-enabled interpreter falls back
    to `cp315-abi3`.

    See the complete [scikit-build-core `abi3t`
    example](https://scikit-build-core.readthedocs.io/en/stable/guide/getting_started.html)
    and CMake's [`FindPython`
    reference](https://cmake.org/cmake/help/v4.4/module/FindPython.html#commands).
    The scikit-build-core example also includes a fallback for CMake versions
    older than 4.4.

=== "meson-python"

    **No released version supports `abi3t` yet.** Support has been merged for a
    future release in [meson-python pull request
    856](https://github.com/mesonbuild/meson-python/pull/856). The released
    [`limited-api`
    setting](https://mesonbuild.com/meson-python/reference/pyproject-settings.html#tool-meson-python-limited-api)
    currently covers ordinary `abi3` only.

    Until support is released, publish version-specific free-threaded wheels.
    If you experiment with an unreleased development version, treat its
    interface as unstable. Meson also cannot yet [select an `abi3t` target from
    a GIL-enabled
    interpreter](https://github.com/mesonbuild/meson/issues/15637).

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
`abi3t`-capable backend, such as the CMake with scikit-build-core path above.
Until meson-python or setuptools support is released, CFFI projects using
those backends should publish version-specific free-threaded wheels.

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
    scikit-build-core, require building with a free-threaded CPython 3.15
    interpreter; others can target it from a GIL-enabled build.
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

This example workflow builds one wheel with free-threaded Python, then installs
the same wheel into both free-threaded and GIL-enabled Python. It covers
`x86_64` Linux in a [PyPA manylinux](https://github.com/pypa/manylinux) image,
`arm64` macOS, and `x64` Windows. The [GitHub-hosted runner
table](https://docs.github.com/en/actions/reference/runners/github-hosted-runners)
documents the architectures used by the macOS and Windows labels.

The example assumes that your project is already configured to produce `abi3t`
wheels and uses `pytest`. Replace the build and test dependencies and commands
to match your project.

<details>
<summary>Complete GitHub Actions cross-test workflow:</summary>

```yaml
name: abi3t cross-test

on:
  pull_request:
  push:

jobs:
  abi3t-wheel:
    name: abi3t cross-test on ${{ matrix.name }}
    runs-on: ${{ matrix.os }}
    container: ${{ matrix.container }}
    strategy:
      fail-fast: false
      matrix:
        include:
          - name: manylinux_x86_64
            os: ubuntu-latest
            container: quay.io/pypa/manylinux_2_28_x86_64
          - name: macos_arm64
            os: macos-15
            architecture: arm64
          - name: windows_x86_64
            os: windows-latest
            architecture: x64

    steps:
      - uses: actions/checkout@v7

      # The manylinux image already contains both interpreters.
      - uses: actions/setup-python@v7
        id: python-ft
        if: ${{ !matrix.container }}
        with:
          python-version: 3.15t
          allow-prereleases: true
          architecture: ${{ matrix.architecture }}

      - uses: actions/setup-python@v7
        id: python-gil
        if: ${{ !matrix.container }}
        with:
          python-version: '3.15'
          allow-prereleases: true
          architecture: ${{ matrix.architecture }}

      - name: Pick the interpreters
        shell: bash
        env:
          IN_CONTAINER: ${{ matrix.container && 'yes' || '' }}
          SETUP_FT: ${{ steps.python-ft.outputs.python-path }}
          SETUP_GIL: ${{ steps.python-gil.outputs.python-path }}
        run: |
          if [ -n "$IN_CONTAINER" ]; then
            echo "FT_PYTHON=/opt/python/cp315-cp315t/bin/python" >>"$GITHUB_ENV"
            echo "GIL_PYTHON=/opt/python/cp315-cp315/bin/python" >>"$GITHUB_ENV"
          else
            echo "FT_PYTHON=$SETUP_FT" >>"$GITHUB_ENV"
            echo "GIL_PYTHON=$SETUP_GIL" >>"$GITHUB_ENV"
          fi

      - name: Build once with free-threaded Python
        shell: bash
        run: |
          "$FT_PYTHON" -Im pip install build
          "$FT_PYTHON" -Im build --wheel

      - name: Select the combined wheel
        shell: bash
        run: |
          ls dist/
          WHEEL=$(find dist -type f | grep -E '/[^/]+-cp315-abi3\.abi3t-[^/]+\.whl$')
          test "$(printf '%s\n' "$WHEEL" | wc -l)" -eq 1
          echo "WHEEL=$WHEEL" >>"$GITHUB_ENV"

      - name: Check the Unix extension suffix
        if: ${{ runner.os != 'Windows' }}
        shell: bash
        run: |
          "$FT_PYTHON" -c '
          import re
          import sys
          import zipfile

          with zipfile.ZipFile(sys.argv[1]) as wheel:
              names = wheel.namelist()

          assert any(
              re.search(r"\.abi3t(?:-[^/]*)?\.so$", name)
              for name in names
          ), names
          ' "$WHEEL"

      - name: Test with free-threaded Python
        shell: bash
        run: |
          "$FT_PYTHON" -Im pip install "$WHEEL" pytest
          "$FT_PYTHON" -Im pytest

      - name: Test the same wheel with GIL-enabled Python
        shell: bash
        run: |
          "$GIL_PYTHON" -Im pip install "$WHEEL" pytest
          "$GIL_PYTHON" -Im pytest
```

</details>

This workflow cross-tests a wheel; it is not a release workflow. The manylinux
job does not repair the wheel or replace [a cibuildwheel release
workflow](ci.md#building-free-threaded-wheels-with-cibuildwheel). In production,
pin third-party actions to commit SHAs and container images to digests.

Python 3.15 is the first release with `abi3t`. Add GIL-enabled and free-threaded
tests for every later Python version you support.

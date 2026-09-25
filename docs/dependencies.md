# Handling dependencies that don’t support free-threading

## Build dependencies that may need special consideration

### CFFI

CFFI 2.0.0 added support for free-threaded Python 3.14. Supporting free-threaded
Python 3.15 requires CFFI 2.1.1 or newer: CFFI 2.1.0 added `abi3t` support, and
CFFI 2.1.1 adapted to a later ABI change in the Python 3.15 beta releases. See
the [CFFI
changelog](https://cffi.readthedocs.io/en/stable/whatsnew.html#v2-1-1) for
details. To support both Python 3.14 and 3.15, install:

```bash
python -m pip install "cffi>=2.1.1"
```

To retain CFFI 2.0.0 as the minimum on Python 3.14, use the following
`pyproject.toml` snippet:

```toml
[build-system]
requires = [
  "cffi>=2.1.1; python_version >= '3.15'",
  "cffi>=2.0.0; python_version >= '3.14' and python_version < '3.15'",
  "cffi; python_version < '3.14'",
]
```

These conditions use the `python_version` [environment
marker](https://packaging.python.org/en/latest/specifications/dependency-specifiers/#environment-markers).
The marker distinguishes Python releases, not GIL configuration, so this also
requires CFFI 2.1.1 or newer on GIL-enabled Python 3.15. You can declare a
runtime dependency in the `project.dependencies` section using the same syntax.

CFFI does not support the free-threaded build of Python 3.13.

### mypyc

The mypyc bindings generator [has preliminary support for the free-threaded
build](https://github.com/mypyc/mypyc/issues/1038#issuecomment-3249330800) in
the `main` branch of mypyc. If you maintain a package that ships binaries using
mypyc, you should try building wheels using the development branch of mypyc. The
maintainers of mypyc encourage users to ship wheels this way and report issues
if they encounter any.

Usually mypyc is used with projects that can be straightforwardly used in a
pure-python mode. If there is no compiled build available, we suggest using a
pure-python build instead.

### Other bindings generators

Cython, nanobind, pybind11, and PyO3 can all build version-specific
free-threaded extensions, although Cython describes its support as
experimental. This does not imply that each project supports the free-threaded
Stable ABI. See [Building and distributing `abi3t` extensions](abi3t.md) for
current `abi3t` workflows and limitations.

## Runtime dependencies that don't support free-threading

### Depending on PyYAML

PyYAML 6.0.3+ supports free-threaded Python starting with Python 3.14t+. If you
**must** support Python 3.13t, you can depend on the [PyYAML-ft fork of
PyYAML](https://pypi.org/project/PyYAML-ft/).

### Other Runtime Dependencies

#### Zstandard

Python 3.14 includes the new [`compression.zstd`
module](https://docs.python.org/3.14/library/compression.zstd.html#module-compression.zstd), backports are available
under [backports.zstd](https://pypi.org/project/backports.zstd/) for Python 3.9-3.13 and can replace the
[zstandard](https://pypi.org/project/zstandard/) package.

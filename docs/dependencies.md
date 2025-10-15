# Handling dependencies that don’t support free-threading

## Build dependencies that may need special consideration

### CFFI

CFFI added support for the free-threaded build of Python 3.14 in version
2.0.0. You can ensure it is installed by passing a version constraint to pip:

```bash
python -m pip install cffi>=2.0.0
```

If you want to force CFFI 2.0.0 to be used as a dependency of a project, you can use the following `pyproject.toml` snippet:

```toml
[build-system]
requires = [
  "cffi>=2.0.0",
]
```

You can also use the `python_version` [environment
marker](https://packaging.python.org/en/latest/specifications/dependency-specifiers/#environment-markers)
to specify the constraint is only valid for Python 3.14 and newer:

```toml
[build-system]
requires = [
  "cffi>=2.0.0; python_version >= '3.14'",
  "cffi; python_version < '3.14'",
]
```

You can declare a runtime dependency in the `project.dependencies` section using
the same syntax.

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

Cython, nanobind, pybind11, and PyO3 all fully support the free-threaded
build. See the documentation of those projects for more details about using them
with the free-threaded interpreter.

## Runtime dependencies that don't support free-threading

### Depending on PyYAML

PyYAML 6.0.3+ support free-threading Python starting with Python 3.14t+. If you
**must** support Python 3.13t, you can depend on the [PyYAML-ft fork of
PyYAML](https://pypi.org/project/PyYAML-ft/).

### Other Runtime Dependencies

#### Zstandard

Python 3.14 includes the new [`compression.zstd`
module](https://docs.python.org/3.14/library/compression.zstd.html#module-compression.zstd), backports are available
under [backports.zstd](https://pypi.org/project/backports.zstd/) for Python 3.9-3.13 and can replace the
[zstandard](https://pypi.org/project/zstandard/) package.

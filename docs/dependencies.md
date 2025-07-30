# Handling dependencies that don’t support free-threading

## Build dependencies that don't support free-threading

### CFFI support for the free-threaded Python build

CFFI added support for the free-threaded build in version 2.0.0b1. You
can install it by passing it a version constraint to pip:

```bash
python -m pip install cffi>=2.0.0b1
```

You can also pass `--pre` to pip but that may also bring in other unwanted
prereleases for projects with big dependency trees.

If you want to force CFFI 2.0.0b1 to be used, you can use the following `pyproject.toml` snippet:

```toml
[build-system]
requires = [
  "cffi>=2.0.0b1",
]
```

You can also use the `python_version` [environment
marker](https://packaging.python.org/en/latest/specifications/dependency-specifiers/#environment-markers)
to specify the constraint is only valid for Python 3.14 and newer:

```toml
[build-system]
requires = [
  "cffi>=2.0.0b1; python_version >= '3.14'",
]
```

You can declare a runtime dependency in the `project.dependencies` section using
the same syntax.

### mypyc

The mypyc bindings generator [does not yet support the free-threaded
build](https://github.com/mypyc/mypyc/issues/1038). Usually mypyc is used with
projects that can be straightforwardly used in a pure-python mode. We suggest
using that and waiting for upstream support in mypyc to get a compiled extension
in the future.

### Other bindings generators

Cython, nanobind, pybind11, and PyO3 all fully support the free-threaded
build. See the documentation of those projects for more details about using them
with the free-threaded interpreter.

## Runtime dependencies that don't support free-threading

### Depending on PyYAML - use PyYAML-ft

If your library depends on [PyYAML](https::/github.com/yaml/pyyaml), you will need
to take extra care to use it with free-threaded Python. PyYAML currently does not
support free-threading and has some thread-safety issues. Its maintainers [have
decided to not port PyYAML](https://github.com/yaml/pyyaml/pull/830#issuecomment-2342475334)
before free-threading and Cython support for it have been more extensively tested.

That's why we've created a fork of PyYAML with support for free-threading called
[PyYAML-ft](https://github.com/Quansight-Labs/pyyaml-ft). PyYAML users can
switch to this fork if they want to test their code with the free-threaded build.

Currently, PyYAML-ft only supports Python 3.13 and 3.13t (i.e. the free-threaded
build of 3.13). To switch to it, you can add the following to your `requirements.txt`:

```requirements.txt
PyYAML; python_version < '3.13'
PyYAML-ft; python_version >= '3.13'
```

If you define your dependencies in `pyproject.toml`, then you can do the following:

```toml
dependencies = [
  "PyYAML; python_version<'3.13'",
  "PyYAML-ft; python_version>='3.13'",
]
```

#### Different module name

PyYAML-ft uses a different module name (namely `yaml_ft`) than upstream PyYAML on
purpose, so that both can be installed in an environment at the same time.

If your library depends on both for different Python versions, you can do the
following for ease of use:

```python
try:
    import yaml_ft as yaml
except ModuleNotFoundError:
    import yaml
```

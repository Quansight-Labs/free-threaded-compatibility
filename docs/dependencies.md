# Handling dependencies that don’t support free-threading

## Build dependencies that don't support free-threading

### CFFI fork with support for free-threading

If your library depends on [CFFI](https://github.com/python-cffi/cffi), there's
some additional work you need to do before you can ship support for the free-threaded
build, since CFFI does not support it yet. Its maintainers [have argued for a
fork themselves](https://github.com/python-cffi/cffi/pull/143#issuecomment-2580781899),
so that free-threading support can be implemented and tested independently
from the upstream package.

There's [a fork under the Quansight-Labs org](https://github.com/Quansight-Labs/cffi)
available, where free-threading support is currently being worked on. If you want to
use this version of CFFI within your own library, you can install it in the
following manner:

```bash
python -m pip install git+https://github.com/Quansight-Labs/cffi.git
```

Keep in mind that support for free-threading in this fork of CFFI is still very
experimental.

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

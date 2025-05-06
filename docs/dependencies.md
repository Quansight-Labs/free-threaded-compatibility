# Handling dependencies that don’t support free-threading

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

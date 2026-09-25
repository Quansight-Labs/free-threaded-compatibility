# Frequently seen errors and how to fix them

These are error messages that we see come up often when working with code or
development workflows that have not been updated to accommodate the
free-threaded build. We also provide suggested fixes. Please send in pull
requests to [the repository for this
document](https://github.com/quansight-labs/free-threaded-compatibility) if you
run into any confusing free-threading-specific errors that you suspect apply to
other libraries and aren't covered here.

## Cython compilation errors: `unknown type name '__pyx_vectorcallfunc'`

This happens if you try to build a Cython extension for the free-threaded build
using a release of Cython that does not support it (< 3.1.0). This might happen
if a package pins an older version of Cython. You should check the build
dependencies of the package and try relaxing any Cython pin or otherwise
establish why the latest Cython release is not being installed at build time.

See [the porting guide](porting.md)
for more details about porting Cython code to work under free-threading.

## What does `RuntimeWarning: The global interpreter lock (GIL) has been enabled` mean?

This happens when Python imports a module defined in a native extension that
does not explicitly declare support for running without the GIL. By default,
native extensions do not support running without the GIL because of the long
history of extensions assuming the GIL locks concurrent access to extension
internals. As a precaution, when the free-threaded Python build imports such an
extension, it assumes that the GIL is *necessary* to run the extension, and
enables the GIL at runtime.

If you have control over the code in the native extension, then you should
update the extension to support the free-threaded build. See [the guide
section](porting-extensions.md) on that topic. If you do not control the
extension or simply want to test running with the GIL disabled despite the
extension not explicitly supporting it, then you can set either the `PYTHON_GIL`
environment variable or the `-X gil` command-line flag for the Python
interpreter to `0` (i.e. the GIL is disabled). This skips the runtime check for
whether extensions support running with the GIL disabled. See the [section on
running free-threaded Python](running-gil-disabled.md) for more details.

## `pip install jupyter` fails

This happens because some of the dependencies of the `jupyter` project on PyPI
do not yet support the free-threaded build. You might see this if you do not
have a compilation environment set up, since dependencies like `PyYAML` do not
ship free-threaded binaries and require from-source compilation.

You also might see errors related to [CFFI] on free-threaded Python 3.13. This
happens because one of Jupyter's dependencies, `argon2-cffi-bindings` uses CFFI
to build a C extension. CFFI 2.0 added support for the free-threaded build, but
only on Python 3.14 and newer. That means that `argon2-cffi-bindings` will never
successfully build on Python 3.13 without some hacking to disable the extension
or force CFFI to build.

For that reason, if you need to use Python 3.13 and Jupyter, we suggest
installing a Jupyter kernel for the free-threaded build into a Jupyter
installation that is installed using a GIL-enabled interpreter. See [the
installation section of this
guide](installing-cpython.md#installing-a-free-threaded-jupyter-kernel) for
instructions to create a new python 3.13t kernel for use in any Jupyter
installation. Alternatively use Python 3.14t.

## What does "Py_LIMITED_API is currently incompatible with Py_GIL_DISABLED" mean?

You may see this error when a build backend does not support using the Limited
API with a free-threaded interpreter. Free-threaded CPython 3.13 and 3.14 do not
have a Stable ABI, so extensions for those versions must use the full C API and
publish a version-specific wheel.

CPython 3.15 adds a separate [Stable ABI for free threading,
`abi3t`](https://docs.python.org/3.15/howto/abi3t-migration.html).
`Py_TARGET_ABI3T` selects this ABI explicitly; when compiling against
free-threaded Python 3.15, defining `Py_LIMITED_API` selects it as well.
Targeting `abi3t` may require source changes, and the build tools must apply the
correct extension suffix and wheel ABI tag. A released build backend without
`abi3t` support may therefore still produce this error on Python 3.15. See
[Building and distributing `abi3t` extensions](abi3t.md) for current backend
support.

If you are building for Python 3.13 or 3.14, or if your extension cannot target
`abi3t`, disable the `Py_LIMITED_API` declaration on free-threaded builds. A
build script can detect a free-threaded build with:

```python
import sysconfig

FREETHREADED_BUILD = bool(sysconfig.get_config_var("Py_GIL_DISABLED"))
```

`FREETHREADED_BUILD` is `False` on a GIL-enabled build and `True` on a
free-threaded build. This fallback produces a version-specific extension rather
than a Stable ABI extension.

## I'm trying to build a library on Windows, but MSVC says "C atomic support is not enabled"

This happens when a C project uses [atomic
operations](porting-extensions.md#lock-free-concurrent-programming-with-atomics)
that are part of the C standard library in the C11 and C17 standards. MSVC does
not yet fully support C standard library atomics, but it does have experimental
support. You can enable it by passing `/experimental:c11atomics` to MSVC as a
compiler option. Precisely how to do this will depend on the project. For an
example in a project that uses setuptools, see [`coveragepy` PR #2020](https://github.com/nedbat/coveragepy/pull/2020/files).

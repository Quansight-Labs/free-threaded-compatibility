## Improving Ecosystem Compatibility with Free-Threaded Python

Quansight Labs is working with the Python runtime team at Meta and stakeholders
across the ecosystem to jumpstart work on converting the libraries that make up
the scientific Python and AI/ML stacks to work with the free-threaded (nogil)
build of CPython 3.13. Additionally, we will look at libraries like PyO3
that are needed to interface with CPython from other languages.

Our initial goal is to ensure libraries at the bottom of the stack like
NumPy, pybind11, and Cython are usable with free-threaded CPython. We will also
be updating packaging tools like meson-python needed to support building wheels
for free-threaded CPython. Once those tools and libraries are in a stable
enough state, we will begin looking at libraries higher in the stack.

### What is this repository?

This repository is for coordinating ecosystem-wide work. We will use
this repository to track, understand, and provide documentation for
dealing with issues that we find are common across many
libraries. Issues that are specific to a project should be reported in
that project's issue tracker.

### Building Free-Threaded CPython

Currently we suggest building CPython from source using the latest version of
the CPython `main` branch. See [the
build
instructions](https://devguide.python.org/getting-started/setup-building/index.html)
in the CPython developer guide. You will need to install [needed third-party
dependencies](https://devguide.python.org/getting-started/setup-building/index.html#install-dependencies)
before building. To build the free-threaded version of CPython, pass
`--disable-gil` to the `configure` script:

```bash
./configure --with-pydebug --disable-gil
```

If you will be switching Python versions often, it may make sense to
build CPython using [pyenv](https://github.com/pyenv/pyenv). See
[the `pyenv` folder](pyenv/README.md) in this repository for more details
managing free-threaded and non-free-threaded Python installs with pyenv.

### Running Python With the GIL disabled

Much of the material in this subsection is also covered in the Python 3.13
[release
notes](https://docs.python.org/3.13/whatsnew/3.13.html#free-threaded-cpython).

You can verify your build has the GIL disabled with the following incantation:

```bash
python -VV
```

If you are using Python 3.13b1 or newer, you should see a message like:

```bash
Python 3.13.0b1+ experimental free-threading build (heads/3.13:d93c4f9, May 21 2024, 10:54:14) [Clang 15.0.0 (clang-1500.1.0.2.5)]
```

Verify that the GIL is disabled at runtime with the following incantation:

```bash
python -c "import sys; print(sys._is_gil_enabled())"
```

Extension modules need to explicitly indicate they support running with the GIL
disabled, otherwise a warning is printed and the GIL is re-enabled at
runtime after importing a module that does not support the GIL. In order to do so,
extension modules that support multi-phase initialization can specify the
[`Py_mod_gil`](https://docs.python.org/3.13/c-api/module.html#c.Py_mod_gil)
module slot like this (the slot has no effect in the non-free-threaded build):

```c
static PyModuleDef_Slot module_slots[] = {
    ...
#ifdef Py_GIL_DISABLED
    {Py_mod_gil, Py_MOD_GIL_NOT_USED},
#endif
    {0, NULL}
};
```

Extensions that use single-phase initialization need to call
[`PyUnstable_Module_SetGIL()`](https://docs.python.org/3.13/c-api/module.html#c.PyUnstable_Module_SetGIL)
in the module's initialization function:

```c
PyMODINIT_FUNC
PyInit__module(void)
{
    PyObject *mod = PyModule_Create(&module);
    if (mod == NULL) {
        return NULL;
    }

#ifdef Py_GIL_DISABLED
    PyModule_ExperimentalSetGIL(mod, Py_MOD_GIL_NOT_USED);
#endif
}
```

To force Python to keep the GIL disabled even after importing a module
that does not support running without it, use the `PYTHON_GIL` environment
variable or the `-X gil` command line option:

```bash
# these are equivalent
PYTHON_GIL=0 python
python -Xgil=0
```

### Porting Extension Modules to Support Free-Threading

Many Python extension modules are not thread-safe in the free-threaded build as
of mid-2024. Up until now, the GIL has added implicit locking around any
operation in Python or C that holds the GIL and the GIL must be explicitly
dropped before many thread-safety issues become problematic. Also, because of
the GIL, attempting to parallelize many workflows using the Python
[threading](https://docs.python.org/3/library/threading.html) module will not
produce any speedups, so thread-safety issues that are possible even with the
GIL are not hit often since users do not make use of threading as much as other
parallelization strategies. This means many codebases have threading bugs that
up-until-now have only been theoretical or present in niche use-cases. With
free-threading, many more users will want to use Python threads.

This means we must analyze the codebases of extension modules to identify
thread-safety issues and make changes to thread-unsafe low-level code,
including C, C++, and Cython code exposed to Python.

#### Suggested Plan of Attack

Put priority on thread-safety issues surfaced by real-world testing. Especially
if there is a lot of low-level code (e.g. most of the C code in NumPy, and
Cython code inside a `with nogil` block) then it's likely that assumptions
about the GIL have introduced thread-safety issues in any real-world code.

The CPython C API exposes the `Py_GIL_DISABLED` macro, which is defined in the
free-threaded build. You can use it to enable code that only runs under the
free-threaded build, isolating possibly performance-impacting changes to the
free-threaded build.

We suggest focusing on safety over single-threaded performance. For example, if
adding locking to a global cache would be more trouble than just disabling it
for a small performance hit, consider doing the simpler thing and disabling the
cache in the free-threaded build. Single-threaded performance can always be
improved later, once you've established free-threaded support and hopefully
improved test coverage for multithreaded workflows.

Definitely run your existing test suite with the GIL disabled, but unless your
tests make heavy use of the `threading` module, you will likely not hit many
issues, so also consider constructing multithreaded tests to expose bugs based
on workflows you want to support. Issues found in these tests are the issues
your users will most likely hit first. The
[`concurrent.futures.ThreadPoolExecutor`](https://docs.python.org/3/library/concurrent.futures.html#concurrent.futures.ThreadPoolExecutor)
class is a lightweight way to create multithreaded tests where many threads
repeatedly call a function simultaneously. You can also use the `threading`
module directly. Adding a `threading.Barrier` before your test code is a good
way to synchronize workers and encourage a race condition.

If you initialize extensions using the C API directly, plan to eventually
support the free-threaded build, and want to encourage people to test it, we
suggest marking that your extensions support disabling the GIL with the
[`Py_mod_gil`
slot](https://docs.python.org/3.13/c-api/module.html#c.Py_mod_gil) for
extensions using multi-phase initialization and
[`PyUnstable_Module_SetGIL()`](https://docs.python.org/3.13/c-api/module.html#c.PyUnstable_Module_SetGIL)
for extensions using single-phase intialization, even if you have not fully
completed porting and testing with the GIL disabled. Cython and `pybind11` do
not yet do this, but currently the plan is for tools wrapping CPython to handle
setting these flags for users, possibly with an override via a configuration
flag.

We are generally assuming users will not do pathological things like resizing an
array while another thread is reading from or writing to it. Eventually we will
need to add locking around data structures to avoid issues like this, but in
this early stage of porting we are not focusing on adding locking on every
operation exposed to users that mutates data.

##### Locking and Synchronization Primitives

If your extension is written in C++, Rust, or another modern language that
exposes locking primitives in the standard library, you should use the locking
primitives provided by your language or framework to add locks when needed.

C does have threading primitives in the standard library, but C compilers do
not uniformly provide `threads.h`. The CPython C API exposes
`PyThread_type_lock`, which provides a portable low-level locking primitive in
the C API. Internally, CPython uses `PyMutex`, a substantially more performant
and memory-efficient mutex, that may be exposed publicly in the future. If that
happens then uses of `PyThread_type_lock` can be replaced with
`PyMutex`. Consider hiding the locking and unlocking details behind a macro or
static inline function to abstract away the underlying locking implementation.

#### Global state

##### Global Settings

* [`threading.local`](https://docs.python.org/3/library/threading.html#thread-local-data).
* [`Py_tss
API`](https://docs.python.org/3/c-api/init.html#thread-specific-storage-tss-api),
also see [PEP 539](https://peps.python.org/pep-0539).
* `thread_local` in C++ or platform-specific equivalent in C

##### Caches

* Disable
* Global locks for single-initializaton
* Per-cache locks if there might be contention
* Atomic initialization flag

#### Shared state

##### Adding thread-safety to data structures

* Shared mutable state is unsafe unless updating the state requires acquiring a
  lock and stopping all other reads and writes while the update happens.
    * Easiest: make more things immutable
    * Locking
    * More sophisticated locking like RW locks.

##### Dealing with thread-unsafe libraries

* Add locking around library usage

   * Re-entrant: Can have a lock per low-level data structure
   * Non-reentrant: Must have a global lock guarding calling the library

#### Cython thread-safety

If your extension is written in Cython, you can generally assume that
"Python-level" code that compiles to CPython C API operations on Python objects
is thread safe, but "C-level" code (e.g. code that will compile inside a `with
nogil` block) may have thread-safety issues. Note that not all code outside
`with nogil` blocks is thread safe. For example, a Python wrapper for a
thread-unsafe C library is thread-unsafe if the GIL is disabled unless there is
locking around uses of the thread-unsafe library. Another example: using
thread-unsafe C-level constructs like a global variable is also thread-unsafe
if the GIL is disabled.

#### CPython C API uses

In the free-threaded build it is possible for the reference count of an object
to change "underneath" a running thread when it is mutated by another
thread. This means that many APIs that assume reference counts cannot be
updated by another thread while it is running are no longer thread safe. In
particular, C code returning "borrowed" references to Python objects in mutable
containers like lists may introduce thread-safety issues. A borrowed reference
happens when a C API function does not increment the reference count of a
Python object before returning the object to the caller. "New" references are
safe to use until the owning thread releases the reference, as in non
free-threaded code.

Most direct uses of the CPython C API are thread safe. There is no need to add
locking for scenarios that should be bugs in CPython. You can assume, for
example, that the initializer for a Python object can only be called by one
thread and the C-level implementation of a Python function can only be called on
one thread. Accessing the arguments of a Python function is thread safe no
matter what C API constructs are used and no matter whether the reference is
borrowed or owned because two threads can't simultaneously call the same
function with the same arguments from the same Python-level context. Of course
it's possible to implement argument parsing in a thread-unsafe manner using
thread-unsafe C or C++ constructs, but it's not possible to do so using the
CPython C API.

##### Unsafe APIs returning borrowed references

The `PyDict` and `PyList` APIs contain many functions returning borrowed
references to items in dicts and lists. Since these containers are mutable,
it's possible for another thread to delete the item from the container, leading
to the item being de-allocated while the borrowed reference is still
"alive". Even code like this:

```C
PyObject *item = Py_NewRef(PyList_GetItem(list_object, 0))
```

Is not thread safe, because in principle it's possible for the list item to be
de-allocated before `Py_NewRef` gets a chance to increment the reference count.

For that reason, you should inspect Python C API code to look for patterns
where a borrowed reference is returned to a shared, mutable data structure, and
replace uses of APIs like `PyList_GetItem` with APIs exposed by the CPython C
API returning strong references like `PyList_GetItemRef`. Not all usages are
problematic (see above) and we do not currently suggest converting all usages of
possibly unsafe APIs returning borrowed references to return new reference. This
would introduce unnecessary reference count churn in situations that are
thread-safe by construction and also likely introduce new reference counting
bugs in C or C++ code using the C API directly. However, many usages *are*
unsafe, and maintaining a borrowed reference to an objects that could be exposed
to another thread is unsafe.

##### Adopt `pythoncapi-compat` to use new C API functions

Rather than maintaining compatibility shims to use functions added to the C API
for Python 3.13 like `PyList_GetItemRef` while maintaining compatibility with
earlier Python versions, we suggest adopting the
[`pythoncapi-compat`](https://github.com/python/pythoncapi-compat) project as a
build-time dependency. This is a header-only library that can be vendored as
e.g. a git submodule and included to expose shims for C API functions on older
versions of Python that do not have implementations.

##### Some low-level APIs don't enforce locking

Some low-level functions like `PyList_SET_ITEM` and `PyTuple_SET_ITEM` do not
do any internal locking and should only be used to build newly created
values. Do *not* use them to modify existing containers in the free-threaded
build.

##### Limited API support

The free-threaded build does not support the limited CPython C API. If you
currently use the limited API you will not be able to use it while shipping
binaries for the free-threaded build. This also means that code inside `#ifdef
Py_GIL_DISABLED` checks can use C API constructs outside the limited API if you
would like to do that, although these uses will need to be removed once the
free-threaded build gains support for compiling with the limited API.

### Continuous Integration

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
          python-version: '3.13.0b2'
          nogil: true
```

You should replace the ellipses with versions for the actions. If there is a
newer CPython 3.13 release available since this document was written or
updated, use that version instead.

The [cibuildwheel](https://cibuildwheel.pypa.io/en/stable/) project has support
for building free-threaded wheels on all platforms. If your project releases
nightly wheels, we suggest configuring cibuildwheel to build nightly
free-threaded wheels.

You will need to specify the following variables in the environment for the
cibuildwheel action:

```
      - name: Build wheels
        uses: pypa/cibuildwheel@...
        env:
          CIBW_PRERELEASE_PYTHONS: True
          CIBW_FREE_THREADED_SUPPORT: True
          CIBW_BUILD: cp313t-${{ matrix.buildplat }}
          # TODO: remove along with installing build deps in
          # cibw_before_build.sh when a released cython can build numpy
          CIBW_BUILD_FRONTEND: "pip; args: --no-build-isolation"
```

As above, replace the ellipses with a `cibuildwheel` version.

If your project depends on Cython, you will need to install a Cython nightly
wheel in the build, as the newest stable release of Cython cannot generate code
that will compile under the free-threaded build. You likely do not need to
disable pip build isolation if your project does not depend on Cython.

The newest pip release does not support installing free-threaded wheels, you
will need to update to pip 24.1b1 or newer to install free-threaded wheels:

```
pip install -U --pre pip
```

You can install nightly wheels for Cython, NumPy, and SciPy using the following
command:

```
pip install -i https://pypi.anaconda.org/scientific-python-nightly-wheels/simple cython
```

Note that nightly wheels may not be available on all platforms yet. Windows
wheels, in particular, are not currently available for NumPy or SciPy.

You will also likely need to manually pass `-Xgil=0` or set `PYTHON_GIL=0` in
your shell environment while running tests to ensure the GIL is actually
disabled during tests, at least until you can register that your extension
modules support disabling the GIL via `Py_mod_gil` and all of your runtime test
dependencies do the same. It is not currently possible to mark that a Cython
module supports running without the GIL.

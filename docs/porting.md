# Porting Extension Modules to Support Free-Threading

Many Python extension modules are not thread-safe in the free-threaded build as
of mid-2024. Up until now, the GIL has added implicit locking around any
operation in Python or C that holds the GIL, and the GIL must be explicitly
dropped before many thread-safety issues become problematic. Also, because of
the GIL, attempting to parallelize many workflows using the Python
[threading](https://docs.python.org/3/library/threading.html) module will not
produce any speedups, so thread-safety issues that are possible even with the
GIL are not hit often since users do not make use of threading as much as other
parallelization strategies. This means many codebases have threading bugs that
up-until-now have only been theoretical or present in niche use cases. With
free-threading, many more users will want to use Python threads.

This means we must analyze the codebases of extension modules to identify
thread-safety issues and make changes to thread-unsafe low-level code,
including C, C++, and Cython code exposed to Python.

### Declaring free-threaded support

Extension modules need to explicitly indicate they support running with the GIL
disabled, otherwise a warning is printed and the GIL is re-enabled at runtime
after importing a module that does not support the GIL. 

C++ extension modules making use of `pybind11` can easily declare support for
running with the GIL disabled via the
[`gil_not_used`](https://pybind11.readthedocs.io/en/stable/reference.html#_CPPv4N7module_23create_extension_moduleEPKcPKcP10module_def16mod_gil_not_used)
argument to `create_extension_module`.

Starting with Cython 3.1.0 (only available via the nightly wheels or the `master`
branch as of right now), extension modules written in Cython can also do so using the
[`freethreading_compatible`](https://cython.readthedocs.io/en/latest/src/userguide/source_files_and_compilation.html#compiler-directives)
compiler directive. It can be enabled either per module as a directive
(`# cython: freethreading_compatible=True`) in `.pyx` files, or globally by adding
`-Xfreethreading_compatible=True` to the Cython arguments via the project's
build system.

Here are a few examples of how to globally enable the directive in a few popular
build systems:

=== "setuptools"

    When using setuptools, you can pass the `compiler_directives` keyword argument
    to `cythonize`:

    ```python
    from Cython.Compiler.Version import version as cython_version
    from packaging.version import Version

    compiler_directives = {}
    if Version(cython_version) >= Version("3.1.0a1"):
        compiler_directives["freethreading_compatible"] = True

    setup(
        ext_modules=cythonize(
            extensions,
            compiler_directives=compiler_directives,
        )
    )
    ```

=== "Meson"

    When using Meson, you can add the directive to the `cython_args` you're
    passing to `py.extension_module`:

    ```meson
    cy = meson.get_compiler('cython')

    cython_args = []
    if cy.version().version_compare('>=3.1.0')
        cython_args += ['-Xfreethreading_compatible=True']
    endif

    py.extension_module('modulename'
        'source.pyx',
        cython_args: cython_args,
        ...
    )
    ```

    You can also globally add the directive for all Cython extension modules:

    ```meson
    cy = meson.get_compiler('cython')
    if cy.version().version_compare('>=3.1.0')
        add_project_arguments('-Xfreethreading_compatible=true', language : 'cython')
    endif
    ```

C or C++ extension modules using multi-phase initialization can specify the
[`Py_mod_gil`](https://docs.python.org/3.13/c-api/module.html#c.Py_mod_gil)
module slot like this:

```c
static PyModuleDef_Slot module_slots[] = {
    ...
#ifdef Py_GIL_DISABLED
    {Py_mod_gil, Py_MOD_GIL_NOT_USED},
#endif
    {0, NULL}
};
```

The `Py_mod_gil` slot has no effect in the non-free-threaded build.

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
    PyUnstable_Module_SetGIL(mod, Py_MOD_GIL_NOT_USED);
#endif
}
```

If you publish binaries and have downstream libraries that depend on your
library, we suggest adding the `Py_mod_gil` slot and uploading nightly wheels
as soon as basic support for the free-threaded build is established in the
development branch. This will ease the work of libraries that depend on yours
to also add support for the free-threaded build.


## Suggested Plan of Attack

Put priority on thread-safety issues surfaced by real-world testing. Run the
test suite for your project and fix any failures that occure only with the GIL
disabled. Some issues may be due to changes in Python 3.13 that are not
specific to the free-threaded build.

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

Many C and C++ extensions assume the GIL serializes access to state shared
between threads, introducing the possibility of data races and race conditions
that were impossible before when the GIL is disabled.

Cython code can also be thread-unsafe and exhibit undefined behavior due to
data races just like any other C or C++ code. However, code operating on Python
objects should not exhibit any low-level data races or undefined behavior due
to Python-level semantics. If you find such a case, it may be a Cython or
CPython bug and should be reported as such. That said, race conditions are
allowed in Python and therefore Cython as well, so you will still need to add
locking or synchronization where appropriate to ensure reproducible results
when running a multithreaded algorithm on shared mutable data.

The CPython C API exposes the `Py_GIL_DISABLED` macro in the free-threaded
build. You can use it to enable low-level code that only runs under the
free-threaded build, isolating possibly performance-impacting changes to the
free-threaded build:

```c
#ifdef Py_GIL_DISABLED
// free-threaded specific code goes here
#endif

#ifndef Py_GIL_DISABLED
// code for gil-enabled builds goes here
#endif
```

We suggest focusing on safety over single-threaded performance. For example, if
adding a lock to a global cache would harm multithreaded scaling, and turning
off the cache implies a a small performance hit, consider doing the simpler
thing and disabling the cache in the free-threaded build. Single-threaded
performance can always be improved later, once you've established free-threaded
support and hopefully improved test coverage for multithreaded workflows.

For NumPy, we are generally assuming users will not do pathological things like
resizing an array while another thread is reading from or writing to it and do
not explicitly account for this. Eventually we will need to add locking around
data structures to avoid races caused by issues like this, but in this early
stage of porting we are not planning to add locking on every operation exposed
to users that mutates data. Locking will likely need to be added in the future,
but that should be done carefully and with experience informed by real-world
multithreaded scaling.

For your libraries, we suggest a similar approach for now. Focus on thread
safety issues that only occur with the GIL disabled. Any non-critical
pre-existing thread safety issues can be dealt with later once the
free-threaded build is used more. The goal for now should be to enable further
refinement and experimentation by fixing issues that prevent using the library
at all.

### Locking and Synchronization Primitives

If your extension is written in C++, Rust, or another modern language that
exposes locking primitives in the standard library, you should consider using
the locking primitives provided by your language or framework to add locks when
needed.

For C code or C-like C++ code, the CPython 3.13 C API exposes
[`PyMutex`](https://docs.python.org/3.13/c-api/init.html#c.PyMutex), a
high-performance locking primitive that supports static allocation. As of
CPython 3.13, the mutex requires only one byte for storage, but future versions
of CPython may change that, so you should not rely on the size of `PyMutex` in
your code.

## Global state

Many CPython C extensions make strong assumptions about the GIL. For example,
before NumPy 2.1.0, the C code in NumPy made extensive use of C static global
variables for storing settings, state, and caches. With the GIL, it is possible
for Python threads to produce non-deterministic results from a calculation, but
it is not possible for two C threads to simultaneously see the state of the C
global variables, so no data races are possible.

In free-threaded Python, global state like this is no longer safe against data
races and undefined behavior in C code. A cache of `PyObject`s stored
in a C global pointer array can be overwritten simultaneously by multiple
Python threads, leading to memory corruption and segfaults.

### Converting to thread local state

Often the easiest way to fix data races due to global state is to convert the
global state to thread local state.

Python and Cython code can make use of
[`threading.local`](https://docs.python.org/3/library/threading.html#thread-local-data)
to declare a thread-local Python object. C and C++ code can also use the
[`Py_tss
API`](https://docs.python.org/3/c-api/init.html#thread-specific-storage-tss-api)
to store thread-local Python object references. [PEP
539](https://peps.python.org/pep-0539) has more details about the `Py_tss` API.

Low-level C or C++ code can make use of the
[`thread_local`](https://en.cppreference.com/w/c/thread/thread_local) storage
specified by recent standard versions. Note that standardization of
thread-local storage in C has been slower than C++, so you may need to use
platform-specific definitions to declare variables with thread-local
storage. Also note that thread-local storage on MSVC has
[caveats](https://learn.microsoft.com/en-us/cpp/parallel/thread-local-storage-tls?view=msvc-170#rules-and-limitations),
and you should not use thread-local storage for anything besides statically
defined integers and pointers.

NumPy has a [`NPY_TLS`
macro](https://github.com/numpy/numpy/blob/b77d2c6cc214cdcde567f356688ebddb2a5e7c8c/numpy/_core/include/numpy/npy_common.h#L116-L128)
in the `numpy/npy_common.h` header. While you can include the numpy header and
use `NPY_TLS` directly on NumPy 2.1 or newer, you can also add the definition
to your own codebase, along with some build configuration tests to test for the
correct definition to use.

### Caches

Global caches are also a common source of thread safety issues. For example, if
a function requires an expensive intermediate result that only needs to be
calculated once, many C extensions store the result in a global variable. This
can lead to data races and memory corruption if more than one thread
simultaneously tries to fill the cache.

If the cache is not critical for performance, consider simply disabling the
cache in the free-threaded build:

```c
static int *cache = NULL;

int my_function_with_a_cache(void) {
    int *my_cache = NULL;
#ifndef Py_GIL_DISABLED
    if (cache == NULL) {
        cache = get_expensive_result();
    }
    my_cache = cache;
#else
    my_cache = get_expensive_result();
#endif;
    // use the cache
}
```

If the cache is set up at import time during module initialization, then you
can assume that module initialization is guaranteed to only happen on one
thread, so you can initialize static globals safely during module
initialization.

```c
static int *cache = NULL;

PyMODINIT_FUNC
PyInit__module(void)
{
    PyObject *mod = PyModule_Create(&module);
    if (mod == NULL) {
        return NULL;
    }

    // don't need to lock or do anything special
    cache = setup_cache();
    
    // do rest of initialization
}
```

If the cache is critical for performance, cannot be generated at import time,
but generally gets filled quickly after a program begins then you will need to
use a single-initialization API to ensure the cache is only ever initialized
once. In C++, use
[`std::once_flag`](https://en.cppreference.com/w/cpp/thread/once_flag) or
[`std::call_once`](https://en.cppreference.com/w/cpp/thread/call_once).

C does not have an equivalent portable API for single initialization. If you
need that, take a look at [this NumPy
PR](https://github.com/numpy/numpy/pull/26780) for an example using atomic
operations and a global mutex.

If the cache is in the form of a data container, then you can lock access to
the container, like in the following example:

```c

#ifdef Py_GIL_DISABLED
static PyMutex cache_lock = {0};
#define LOCK() PyMutex_Lock(&cache_lock)
#define UNLOCK() PyMutex_Unlock(&cache_lock)
#else
#define LOCK()
#define UNLOCK()
#endif

static int *cache = NULL;
static PyObject *global_table = NULL;

int initialize_table(void) {
    // called during module initialization
    global_table = PyDict_New();
    return;
}

int function_accessing_the_cache(void) {
    LOCK();
    // use the cache
    
    UNLOCK();
}

```

### Dealing with thread-unsafe libraries

Many C, C++, and Fortran libraries are not written in a thread-safe manner. It
is still possible to call these libraries from free-threaded Python, but
wrappers must add appropriate locks to prevent undefined behavior.

There are two kinds of thread unsafe libraries: reentrant and non-reentrant. A
reentrant library generally will expose state as a struct that must be passed
to library functions. So long as the state struct is not shared between
threads, functions in the library can be safely executed simultaneously.

Wrapping reentrant libraries requires adding locking whenever the state struct
is accessed.

```c
typedef struct lib_state_struct {
    low_level_library_state *state;
    PyMutex lock;
} lib_state_struct;

int call_library_function(lib_state_struct *lib_state) {
    PyMutex_Lock(lib_state->lock);
    library_function(lib_state->state);
    PyMutex_Unlock(lib_state->lock)
}

int call_another_library_function(lib_state_struct *lib_state) {
    PyMutex_Lock(lib_state->lock);
    another_library_function(lib_state->state);
    PyMutex_Unlock(lib_state->lock)
}
```

With this setup, if two threads call `library_function` and
`another_library_functions` simultaneously, one thread will block until the
other thread finishes, preventing concurrent access to `lib_state->state`.

Non-reentrant libraries provide an even weaker guarantee: threads cannot
call library functions simultaneously without causing undefined
behavior. Generally this is due to use of global static state in the
library. This means that non-reentrant libraries require a global lock:

```c

static PyMutex global_lock = {0};

int call_library_function(int *argument) {
    PyMutex_Lock(global_lock);
    library_function(argument);
    PyMutex_Unlock(global_lock);
}
```

Any other wrapped function needs similar locking around each call into the
library.

### Dealing with thread-unsafe objects

Similar to the section above, objects may need locking or atomics if they can
be concurrently modified from multiple threads. CPython 3.13
exposes a public C API that allows users to use the built-in
per-object locks.

For example the following code:
```C
int do_modification(MyObject *obj) {
    return modification_on_obj(obj);
}
```

Should be transformed to:
```C
int do_modification(MyObject *obj) {
    int res;
    Py_BEGIN_CRTIICAL_SECTION(obj);
    res = modification_on_obj(obj);
    Py_END_CRTIICAL_SECTION(obj);
    return res;
}
```

A variant for locking two objects at once is also available. For more information
about `Py_BEGIN_CRITICAL_SECTION`, please see the
[Python C API documentation on critical sections](https://docs.python.org/3.13/c-api/init.html#python-critical-section-api).


## Cython thread-safety

If your extension is written in Cython, you can generally assume that
"Python-level" code that compiles to CPython C API operations on Python objects
is thread safe, but "C-level" code (e.g. code that will compile inside a `with
nogil` block) may have thread-safety issues. Note that not all code outside
`with nogil` blocks is thread safe. For example, a Python wrapper for a
thread-unsafe C library is thread-unsafe if the GIL is disabled unless there is
locking around uses of the thread-unsafe library. Another example: using
thread-unsafe C-level constructs like a global variable is also thread-unsafe
if the GIL is disabled.

## CPython C API usage

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

### Unsafe APIs returning borrowed references

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

### Adopt `pythoncapi-compat` to use new C API functions

Rather than maintaining compatibility shims to use functions added to the C API
for Python 3.13 like `PyList_GetItemRef` while maintaining compatibility with
earlier Python versions, we suggest adopting the
[`pythoncapi-compat`](https://github.com/python/pythoncapi-compat) project as a
build-time dependency. This is a header-only library that can be vendored as
e.g. a git submodule and included to expose shims for C API functions on older
versions of Python that do not have implementations.

### Some low-level APIs don't enforce locking

Some low-level functions like `PyList_SET_ITEM` and `PyTuple_SET_ITEM` do not
do any internal locking and should only be used to build newly created
values. Do *not* use them to modify existing containers in the free-threaded
build.

### Limited API support

The free-threaded build does not support the limited CPython C API. If you
currently use the limited API you will not be able to use it while shipping
binaries for the free-threaded build. This also means that code inside `#ifdef
Py_GIL_DISABLED` checks can use C API constructs outside the limited API if you
would like to do that, although these uses will need to be removed once the
free-threaded build gains support for compiling with the limited API.

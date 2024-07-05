## Running Python With the GIL disabled

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
    PyUnstable_Module_SetGIL(mod, Py_MOD_GIL_NOT_USED);
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

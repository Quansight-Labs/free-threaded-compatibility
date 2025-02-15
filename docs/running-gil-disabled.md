# Running Python with the GIL Disabled

!!! info

    Most of the content on this page is also covered in the Python 3.13
    [release notes](https://docs.python.org/3.13/whatsnew/3.13.html#free-threaded-cpython).

!!! note

    The free-threaded Python executable will always have a `python3.13t` alias
    (for Python 3.13); whether `python`, `python3` and/or `python3.13` point at
    the free-threaded executable or not will depend on the installation method
    (see [the install guide](installing_cpython.md) for more details).

    For example, the Python 3.13 Windows installer from python.org
    installs the free-threaded binary as `python3.13t.exe` (with a "t" suffix
    to indicate it is "t"hreaded), whereas the standard GIL-enabled Python
    binary is simply named `python.exe` (as usual). If you cannot find the
    free-threaded binary, that means the free-threaded option was not selected
    during installation.

You can verify if your build of CPython itself has the GIL disabled with the
following incantation:

```bash
python -VV
```

If you are using Python 3.13b1 or newer, you should see a message like:

```bash
Python 3.13.1 experimental free-threading build (main, Dec 10 2024, 14:07:41) [Clang 16.0.0 (clang-1600.0.26.4)]
```

To verify whether the GIL is disabled at runtime or not, you can use this in
your code:

```python
import sys

sys._is_gil_enabled()
```

This will be `True` on the free-threaded build when the GIL is re-enabled at
runtime, but should be `False` before importing any packages. Note that
`sys._is_gil_enabled()` is only available on Python 3.13 and newer, you will
see an `AttributeError` on older Python versions.

To force Python to keep the GIL disabled even after importing a module
that does not support running without it, use the `PYTHON_GIL` environment
variable or the `-X gil` command line option:

```bash
# these are equivalent
PYTHON_GIL=0 python
python -Xgil=0
```

To check whether the Python interpreter you're using is a free-threaded build,
irrespective of whether the GIL was re-enabled at runtime or not, you can use
this within your code:

```python
import sysconfig

is_freethreaded = bool(sysconfig.get_config_var("Py_GIL_DISABLED"))
```

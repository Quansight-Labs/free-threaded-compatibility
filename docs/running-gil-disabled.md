# Running with the GIL disabled

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


You can verify your build of CPython itself has the GIL disabled with the
following incantation:

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

To force Python to keep the GIL disabled even after importing a module
that does not support running without it, use the `PYTHON_GIL` environment
variable or the `-X gil` command line option:

```bash
# these are equivalent
PYTHON_GIL=0 python
python -Xgil=0
```

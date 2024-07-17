# Running with the GIL disabled

!!! info
    Most of the content on this page is also covered in the Python 3.13
    [release notes](https://docs.python.org/3.13/whatsnew/3.13.html#free-threaded-cpython).

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

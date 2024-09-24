# Compatibility status tracking

This page tracks the status of packages for which we're aware of active work on
free-threaded support. It contains packages with extension modules, as well
as build tools and packages that needed code specifically to support
free-threading. Note that pure Python code works without changes by design,
hence this page does not aim to track pure Python packages.

If there's a bug related to free-threading in a library you use, please open
an issue on the corresponding issue tracker or post a comment on the
corresponding free-threading support tracking issue (see table below). If
an issue spans multiple projects or there's an ecosystem-wide point to discuss,
please open an issue on [this issue tracker](https://github.com/Quansight-Labs/free-threaded-compatibility/issues).

!!! tip
    It's early days for free-threaded support - bugs in CPython itself and in
    widely used libraries with extension modules are being fixed every week.
    It may be useful to use nightly wheels (when available) of packages
    like `cython` or `numpy`, even if a first release is available on PyPI.
    For example, you can install a NumPy nightly wheel by running:

    ```bash
    pip install -i https://pypi.anaconda.org/scientific-python-nightly-wheels/simple numpy
    ```

<!-- keep alphabetically ordered -->

| Project           |                                Upstream issue                                |     Tested in CI      |     PyPI release      | First version with support |                       Nightly wheels                       |                                       Nightly link                                       |
| :---------------- | :--------------------------------------------------------------------------: | :-------------------: | :-------------------: | :------------------------: | :--------------------------------------------------------: | :--------------------------------------------------------------------------------------: |
| cffi              |      [:simple-github:](https://github.com/python-cffi/cffi/issues/126)       | :material-check-bold: |                       |            1.18            |                                                            |                                                                                          |
| cibuildwheel      |     [:simple-github:](https://github.com/pypa/cibuildwheel/issues/1657)      | :material-check-bold: | :material-check-bold: |            2.19            |                                                            |                                                                                          |
| CMake             |                                                                              |                       | :material-check-bold: |      3.30.0 [^cmake]       |                                                            |                                                                                          |
| ContourPy         |     [:simple-github:](https://github.com/contourpy/contourpy/issues/407)     | :material-check-bold: |                       |           1.3.0            |               :simple-linux: :simple-apple:                |  [:simple-anaconda:](https://anaconda.org/scientific-python-nightly-wheels/contourpy/)   |
| Cython            |       [:simple-github:](https://github.com/cython/cython/issues/6221)        | :material-check-bold: |                       |           3.1.0            | :simple-linux: :simple-apple: :material-microsoft-windows: |    [:simple-anaconda:](https://anaconda.org/scientific-python-nightly-wheels/cython/)    |
| joblib            |       [:simple-github:](https://github.com/joblib/joblib/issues/1592)        | :material-check-bold: | :material-check-bold: |           1.4.2            |                                                            |                                                                                          |
| matplotlib        |   [:simple-github:](https://github.com/matplotlib/matplotlib/issues/28611)   | :material-check-bold: | :material-check-bold: |           3.9.0            |               :simple-linux: :simple-apple:                |  [:simple-anaconda:](https://anaconda.org/scientific-python-nightly-wheels/matplotlib/)  |
| Meson             |     [:simple-github:](https://github.com/mesonbuild/meson/issues/13263)      |                       | :material-check-bold: |           1.5.0            |                                                            |                                                                                          |
| meson-python      |   [:simple-github:](https://github.com/mesonbuild/meson-python/issues/499)   | :material-check-bold: | :material-check-bold: |           0.16.0           |                                                            |                                                                                          |
| multidict         |     [:simple-github:](https://github.com/aio-libs/multidict/issues/1014)     |                       |                       |                            |                                                            |                                                                                          |
| mypyc             |        [:simple-github:](https://github.com/mypyc/mypyc/issues/1038)         |                       |                       |                            |                                                            |                                                                                          |
| Nuitka            |       [:simple-github:](https://github.com/Nuitka/Nuitka/issues/3062)        |                       |                       |                            |                                                            |                                                                                          |
| NumPy             |        [:simple-github:](https://github.com/numpy/numpy/issues/26157)        | :material-check-bold: | :material-check-bold: |           2.1.0            |               :simple-linux: :simple-apple:                |    [:simple-anaconda:](https://anaconda.org/scientific-python-nightly-wheels/numpy/)     |
| packaging         |       [:simple-github:](https://github.com/pypa/packaging/issues/727)        | :material-check-bold: | :material-check-bold: |            24.0            |                                                            |                                                                                          |
| pandas            |     [:simple-github:](https://github.com/pandas-dev/pandas/issues/59057)     | :material-check-bold: |                       |           3.0.0            |               :simple-linux: :simple-apple:                |                                                                                          |
| Pillow            |    [:simple-github:](https://github.com/python-pillow/Pillow/issues/8199)    | :material-check-bold: |                       |           11.0.0           | :simple-linux: :simple-apple: :material-microsoft-windows: |    [:simple-anaconda:](https://anaconda.org/scientific-python-nightly-wheels/pillow/)    |
| pip               |         [:simple-github:](https://github.com/pypa/pip/issues/12634)          | :material-check-bold: | :material-check-bold: |            24.1            |                                                            |                                                                                          |
| PyArrow           |       [:simple-github:](https://github.com/apache/arrow/issues/43536)        | :material-check-bold: |                       |           18.0.0           |               :simple-linux: :simple-apple:                |   [:simple-anaconda:](https://anaconda.org/scientific-python-nightly-wheels/pyarrow/)    |
| pybind11          |      [:simple-github:](https://github.com/pybind/pybind11/issues/5112)       | :material-check-bold: | :material-check-bold: |            2.13            |                                                            |                                                                                          |
| PyO3              |         [:simple-github:](https://github.com/PyO3/pyo3/issues/4265)          | :material-check-bold: |          N/A          |           0.22.2           |                            N/A                             |                                           N/A                                            |
| PyWavelets        |                                                                              | :material-check-bold: | :material-check-bold: |           1.7.0            |               :simple-linux: :simple-apple:                |  [:simple-anaconda:](https://anaconda.org/scientific-python-nightly-wheels/pywavelets/)  |
| scikit-build-core |                                                                              | :material-check-bold: | :material-check-bold: |           0.9.5            |                                                            |                                                                                          |
| scikit-image      | [:simple-github:](https://github.com/scikit-image/scikit-image/issues/7464)  | :material-check-bold: |                       |                            |                                                            |                                                                                          |
| scikit-learn      | [:simple-github:](https://github.com/scikit-learn/scikit-learn/issues/28978) | :material-check-bold: |                       |           1.6.0            |                       :simple-linux:                       | [:simple-anaconda:](https://anaconda.org/scientific-python-nightly-wheels/scikit-learn/) |
| SciPy             |        [:simple-github:](https://github.com/scipy/scipy/issues/20669)        | :material-check-bold: |                       |           1.15.0           |               :simple-linux: :simple-apple:                |    [:simple-anaconda:](https://anaconda.org/scientific-python-nightly-wheels/scipy/)     |
| setuptools        |                                                                              | :material-check-bold: | :material-check-bold: |           69.5.0           |                                                            |                                                                                          |
| zstandard         |  [:simple-github:](https://github.com/indygreg/python-zstandard/issues/231)  |                       |                       |                            |                                                            |                                                                                          |

[^cmake]: Windows isn't correctly handled yet in CMake 3.30.0, see [cmake#26016](https://gitlab.kitware.com/cmake/cmake/-/issues/26016)

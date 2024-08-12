# Compatibility status tracking

This page tracks the status of packages for which we're aware of active work on
free-threaded support. It contains packages with extension modules, as well
as build tools and packages that needed code specifically to support
free-threading. Note that pure Python code works without changes by design,
hence this page does not aim to track pure Python packages.

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

| Project           |     Tested in CI      |          PyPI release          | First version with support |                       Nightly wheels                       |                                       Nightly link                                       |
| :---------------- | :-------------------: | :----------------------------: | :------------------------: | :--------------------------------------------------------: | :--------------------------------------------------------------------------------------: |
| cibuildwheel      | :material-check-bold: |     :material-check-bold:      |            2.19            |                                                            |                                                                                          |
| CMake             |                       |     :material-check-bold:      |      3.30.0 [^cmake]       |                                                            |                                                                                          |
| ContourPy         | :material-check-bold: |                                |           1.3.0            |               :simple-linux: :simple-apple:                |  [:simple-anaconda:](https://anaconda.org/scientific-python-nightly-wheels/contourpy/)   |
| Cython            | :material-check-bold: |                                |           3.1.0            | :simple-linux: :simple-apple: :material-microsoft-windows: |    [:simple-anaconda:](https://anaconda.org/scientific-python-nightly-wheels/cython/)    |
| joblib            | :material-check-bold: |     :material-check-bold:      |           1.4.2            |                                                            |                                                                                          |
| Meson             |                       |     :material-check-bold:      |           1.5.0            |                                                            |                                                                                          |
| meson-python      | :material-check-bold: |     :material-check-bold:      |           0.16.0           |                                                            |                                                                                          |
| NumPy             | :material-check-bold: | :material-check-bold: [^numpy] |           2.1.0            |               :simple-linux: :simple-apple:                |    [:simple-anaconda:](https://anaconda.org/scientific-python-nightly-wheels/numpy/)     |
| packaging         | :material-check-bold: |     :material-check-bold:      |            24.0            |                                                            |                                                                                          |
| pandas            | :material-check-bold: |                                |           3.0.0            |               :simple-linux: :simple-apple:                |                                                                                          |
| Pillow            | :material-check-bold: |                                |           11.0.0           | :simple-linux: :simple-apple: :material-microsoft-windows: |    [:simple-anaconda:](https://anaconda.org/scientific-python-nightly-wheels/pillow/)    |
| pip               | :material-check-bold: |     :material-check-bold:      |            24.1            |                                                            |                                                                                          |
| pybind11          | :material-check-bold: |     :material-check-bold:      |            2.13            |                                                            |                                                                                          |
| PyWavelets        | :material-check-bold: |                                |           1.7.0            |               :simple-linux: :simple-apple:                |  [:simple-anaconda:](https://anaconda.org/scientific-python-nightly-wheels/pywavelets/)  |
| scikit-build-core | :material-check-bold: |     :material-check-bold:      |           0.9.5            |                                                            |                                                                                          |
| scikit-learn      | :material-check-bold: |                                |           1.6.0            |                       :simple-linux:                       | [:simple-anaconda:](https://anaconda.org/scientific-python-nightly-wheels/scikit-learn/) |
| SciPy             | :material-check-bold: |                                |           1.15.0           |               :simple-linux: :simple-apple:                |    [:simple-anaconda:](https://anaconda.org/scientific-python-nightly-wheels/scipy/)     |
| setuptools        | :material-check-bold: |     :material-check-bold:      |           69.5.0           |                                                            |                                                                                          |

[^cmake]: Windows isn't correctly handled yet in CMake 3.30.0, see [cmake#26016](https://gitlab.kitware.com/cmake/cmake/-/issues/26016)

[^numpy]: Currently available as the NumPy 2.1.0rc1 prerelease. Install by
    passing `--pre` to pip.

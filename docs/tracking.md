# Compatibility status tracking



| Project       | Tested in CI     | PyPI release    | First version with support    | Nightly wheels    | Nightly link    |
|:--------------|:----------------:|:---------------:|:-----------------------------:|:-----------------:|:---------------:|
| cibuildwheel   | :material-check-bold: |   :material-check-bold:   | 2.19   |    |    |
| CMake    |    | :material-check-bold:    | 3.30.0 [^cmake]   |    |    |
| Cython       | :material-check-bold: |              | 3.1.0                      | :simple-linux: :simple-apple: :material-microsoft-windows: | [:simple-anaconda:](https://anaconda.org/scientific-python-nightly-wheels/cython/)       |
| Meson   |  | `--pre`    | 1.5.0 [^meson]   |    |    |
| meson-python   | :material-check-bold: |   :material-check-bold:   | 0.16.0   |    |    |
| NumPy        | :material-check-bold: |              | 2.1.0                      | :simple-linux: :simple-apple:                              | [:simple-anaconda:](https://anaconda.org/scientific-python-nightly-wheels/numpy/)        |
| packaging   | :material-check-bold: | :material-check-bold:   | 24.0   |   |   |
| pandas       | :material-check-bold: |   | 3.0.0    |    |    |
| Pillow       | :material-check-bold: ||    |    |    |    |
| pip   | :material-check-bold: | :material-check-bold:   | 24.1   |    |    |
| pybind11   | :material-check-bold: | :material-check-bold:   | 2.13   |    |    |
| PyWavelets   | :material-check-bold: |    | 1.7.0   | :simple-linux: :simple-apple:   | [:simple-anaconda:](https://anaconda.org/scientific-python-nightly-wheels/pywavelets/)   |
| scikit-build-core   | :material-check-bold: | :material-check-bold:   | 0.9.5  |    |    |
| scikit-learn | :material-check-bold: |     | 1.6.0    | :simple-linux:   | [:simple-anaconda:](https://anaconda.org/scientific-python-nightly-wheels/scikit-learn/) |
| SciPy        | :material-check-bold: |     | 1.15.0   | :simple-linux: :simple-apple:    | [:simple-anaconda:](https://anaconda.org/scientific-python-nightly-wheels/scipy/)        |
| setuptools   | :material-check-bold: | :material-check-bold:   | 69.5.0   |    |    |



[^cmake]:
    Windows isn't correctly handled yet in CMake 3.30.0, see [cmake#26016](https://gitlab.kitware.com/cmake/cmake/-/issues/26016)

[^meson]:
    Meson 1.5.0 is only needed for Windows support, older versions work fine for all other platforms

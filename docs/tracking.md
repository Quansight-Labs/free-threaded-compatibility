# Compatibility status tracking



| Project       | Tested in CI     | Nightly wheels    | Nightly link    | PyPI release    | First version with support    |
|:--------------|:----------------:|:-----------------:|:---------------:|:---------------:|:-----------------------------:|
| cibuildwheel   | :material-check-bold: |   |   |   :material-check-bold:   | 2.19   |
| Cython       | :material-check-bold: | :simple-linux: :simple-apple: :material-microsoft-windows: | [:simple-anaconda:](https://anaconda.org/scientific-python-nightly-wheels/cython/)       |              | 3.1.0                      |
| Meson   |  |   |   | `--pre`    | 1.5.0 [^meson]   |
| meson-python   | :material-check-bold: |   |   |   :material-check-bold:   | 0.16.0   |
| NumPy        | :material-check-bold: | :simple-linux: :simple-apple:                              | [:simple-anaconda:](https://anaconda.org/scientific-python-nightly-wheels/numpy/)        |              | 2.1.0                      |
| packaging   | :material-check-bold: |   |   |   :material-check-bold:   | 24.0   |
| pandas       | :material-check-bold: |                                                            |                                                                                          |              | 3.0.0                      |
| Pillow       | :material-check-bold: |                                                            |                                                                                          |              |                            |
| pip   | :material-check-bold: |   |   |   :material-check-bold:   | 24.1   |
| pybind11   | :material-check-bold: |   |   |   :material-check-bold:   | 2.13   |
| PyWavelets   | :material-check-bold: | :simple-linux: :simple-apple:                              | [:simple-anaconda:](https://anaconda.org/scientific-python-nightly-wheels/pywavelets/)   |              | 1.7.0                      |
| scikit-build-core   | :material-check-bold: |   |   |   :material-check-bold:   | 0.9.5  |
| scikit-learn | :material-check-bold: | :simple-linux:                                             | [:simple-anaconda:](https://anaconda.org/scientific-python-nightly-wheels/scikit-learn/) |              | 1.6.0                      |
| SciPy        | :material-check-bold: | :simple-linux: :simple-apple:                              | [:simple-anaconda:](https://anaconda.org/scientific-python-nightly-wheels/scipy/)        |              | 1.15.0                     |
| setuptools   | :material-check-bold: |   |   |   :material-check-bold:   | 69.5.0   |




[^meson]:
    Meson 1.5.0 is only needed for Windows support, older versions work fine for all other platforms

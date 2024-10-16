# Installing a free-threaded Python

To install a free-threaded CPython interpreter, you can either use a pre-built
binary or build CPython from source. The former is quickest to get started
with. Building from source is not too difficult either though, and in case you
hit a bug that may involve CPython itself then you may want to build from
source.

## Binary install options

There are a growing number of options to install a free-threaded interpreter,
from the python.org installers to Linux distro and Conda package managers.

!!! note
    For any of these options, please check after the install succeeds that you
    have a `pip` version that is recent enough (`>=24.1`), and upgrade it if
    that isn't the case. Older `pip` versions will select wheels with the
    `cp313` tag (binary-incompatible) rather than the `cp313t` tag.

??? question "As a packager, what should I name the package and interpreter?"
    Please see [this guidance from the Python Steering Council](https://github.com/python/steering-council/issues/221#issuecomment-1841593283)

### python.org installers

The [python.org downloads page](https://www.python.org/download/pre-releases/)
provides macOS and Windows installers that have experimental support. Note
that you have to customize the install - e.g., for Windows there is a
_Download free-threaded binaries_ checkbox under "Advanced Options".
See also the [Using Python on Windows](https://docs.python.org/3.13/using/windows.html#installing-free-threaded-binaries)
section of the Python 3.13 docs.

Automating the process of downloading the official installers
and installing the free-threaded binaries is also possible:

=== "Windows"
    On Windows, you can invoke the installer from the command-line prompt:

    ```powershell
    $url = 'https://www.python.org/ftp/python/3.13.0/python-3.13.0-amd64.exe'
    Invoke-WebRequest -Uri $url -OutFile 'python.exe'
    python.exe /quiet Include_freethreaded=1
    ```

    If you are running this script without administrator privileges,
    a UAC prompt will trigger when you try to run the installer.
    The resulting Python installation will be available afterwards
    in `AppData\Local\Programs\Python\Python313\python3.13t.exe`.
    See [Installing Without UI](https://docs.python.org/3.13/using/windows.html#installing-without-ui)
    for more information.

=== "macOS"
    On macOS, you can use `installer` to install a macOS package you've
    downloaded:

    ```bash
    curl -O https://www.python.org/ftp/python/3.13.0/python-3.13.0-macos11.pkg

    # create installer choice changes to customize the install:
    #    enable the PythonTFramework-3.13 package
    #    while accepting the other defaults (install all other packages)
    cat > ./choicechanges.plist <<EOF
    <?xml version="1.0" encoding="UTF-8"?>
    <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
    <plist version="1.0">
    <array>
            <dict>
                    <key>attributeSetting</key>
                    <integer>1</integer>
                    <key>choiceAttribute</key>
                    <string>selected</string>
                    <key>choiceIdentifier</key>
                    <string>org.python.Python.PythonTFramework-3.13</string>
            </dict>
    </array>
    </plist>
    EOF

    sudo installer -pkg ./python-3.13.0-macos11.pkg \
        -applyChoiceChangesXML ./choicechanges.plist \
        -target /
    rm -f python-3.13.0-macos11.pkg
    ```

    See also [this Github issue](https://github.com/python/cpython/issues/120098)
    for more information.

### Linux distros

=== "Fedora"
    Fedora ships a packaged version, which you can install with:

    ```bash
    sudo dnf install python3.13-freethreading
    ```

    This will install the interpreter at `/usr/bin/python3.13t`.

=== "Nixpkgs"
    Nixpkgs provides cached builds under the [`python313FreeThreading`](https://search.nixos.org/packages?channel=unstable&show=python313FreeThreading&type=packages)
    attribute from NixOS 24.05 and newer.

    With `flakes` enabled the following command will drop you in an ephemeral shell:

    ```bash
    nix shell nixpkgs#python313FreeThreading
    ```

    Without `flakes`, make sure to update your nixpkgs channel first:

    ```bash
    sudo nix-channel --update
    nix-shell -p python313FreeThreading
    ```

=== "Ubuntu"
    For Ubuntu you can use the [deadsnakes PPA](https://launchpad.net/%7Edeadsnakes/+archive/ubuntu/ppa/+packages)
    by adding it to your repositories and then installing `python3.13-nogil`:

    ```bash
    sudo add-apt-repository ppa:deadsnakes
    sudo apt-get update
    sudo apt-get install python3.13-nogil
    ```

### Conda Packages

=== "Conda-forge"
    ```bash
    mamba create -n nogil -c conda-forge python-freethreading
    ```

    or with conda:

    ```bash
    conda create -n nogil --override-channels -c conda-forge python-freethreading
    ```

=== "Anaconda Testing"
    Anaconda's test channel includes the Python interpreter and ABI-compatible
    builds of many common packages, like NumPy, Cython, Pandas, etc.  These
    packages use the `python_abi` metapackage and should be compatible with
    conda-forge:

    ```bash
    conda create -n nogil --override-channels -c ad-testing/label/py313 -c https://repo.anaconda.com/pkgs/main python-freethreading
    ```

    [Full list of Anaconda test packages built with free-threading ABI.](https://anaconda.org/ad-testing/repo?label=py313_nogil&type=any)

## Containers

The [manylinux containers](https://github.com/pypa/manylinux) have free-threaded
builds. You can use any of the actively supported images:

- `quay.io/pypa/manylinux2014_...`
- `quay.io/pypa/manylinux_2_28_...`
- `quay.io/pypa/musllinux_1_1_...`
- `quay.io/pypa/musllinux_1_2_...`

Replace `...` with your desired architecture, such as `x86_64` or `aarch64`.

These images have `python3.13t` available, along with other commonly used tools
that can target it like the latest `pip`, `pipx`, and `uv`.

## Building from source

Currently we suggest building CPython from source using the latest version of
the CPython `main` branch. See
[the build instructions](https://devguide.python.org/getting-started/setup-building/index.html)
in the CPython developer guide. You will need to install [needed third-party
dependencies](https://devguide.python.org/getting-started/setup-building/index.html#install-dependencies)
before building. To build the free-threaded version of CPython, pass
`--disable-gil` to the `configure` script:

```bash
./configure --with-pydebug --disable-gil
```

If you will be switching Python versions often, it may make sense to
build CPython using [pyenv](https://github.com/pyenv/pyenv). In order to
do that, you can use the following:

```bash
pyenv install --debug --keep 3.13.0
```

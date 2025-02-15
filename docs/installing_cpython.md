# Installing Free-Threaded Python

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

### python.org and nuget installers

The [python.org downloads page](https://www.python.org/download/pre-releases/)
provides macOS and Windows installers that have experimental support.

Note that you have to customize the install - e.g., for Windows there is a
_Download free-threaded binaries_ checkbox under "Advanced Options". See also
the [Using Python on
Windows](https://docs.python.org/3.13/using/windows.html#installing-free-threaded-binaries)
section of the Python 3.13 docs.

Automating the process of downloading the official installers
and installing the free-threaded binaries is also possible:

=== "Windows"

    Due to limitations of the Windows Python.org installer, using free-threaded Python
    installed from the Python.org installer may lead to trouble. In particular, if you
    install both a free-threaded and gil-enabled build of Python 3.13 using the Python.org
    installer, both installs will share a `site-packages` folder. This can very quickly
    lead to broken environments if packages for both versions are simultaneously installed.

    For that reason, we suggest using the `nuget` installer, which provides a
    separate `python-freethreaded` package that does not share an installation
    with the `python` package.

    ```powershell
    $url = 'https://www.nuget.org/api/v2/package/python-freethreaded/3.13.1'
    Invoke-WebRequest -Uri $url -OutFile 'python-freethreaded.3.13.1.nupkg'
    Install-Package python-freethreaded -Scope CurrentUser -Source $pwd
    $python_dir = (Get-Item((Get-Package -Name python-freethreaded).Source)).DirectoryName
    $env:path = $python_dir + "\tools;" + $python_dir + "\tools\Scripts;" + $env:Path
    ```

    This will only modify your Path for the current Powershell session, so you
    will also need to permanently add the nuget package location to your Path to
    use it after closing the current session.

    If for some reason you *need* to use the Python.org installer, despite the problems
    described above, you can install it like so:

    ```powershell
    $url = 'https://www.python.org/ftp/python/3.13.1/python-3.13.1-amd64.exe'
    Invoke-WebRequest -Uri $url -OutFile 'python-3.13.1-amd64.exe'
    .\python-3.13.1-amd64.exe /quiet Include_freethreaded=1
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
    curl -O https://www.python.org/ftp/python/3.13.1/python-3.13.1-macos11.pkg

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

    sudo installer -pkg ./python-3.13.1-macos11.pkg \
        -applyChoiceChangesXML ./choicechanges.plist \
        -target /
    rm -f python-3.13.1-macos11.pkg
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

### Multi-platform Package Managers

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
    builds of many common packages, like NumPy, Cython, Pandas, etc. These
    packages use the `python_abi` metapackage and should be compatible with
    conda-forge:

    ```bash
    conda create -n nogil --override-channels -c ad-testing/label/py313 -c https://repo.anaconda.com/pkgs/main python-freethreading
    ```

    [Full list of Anaconda test packages built with free-threading ABI.](https://anaconda.org/ad-testing/repo?label=py313_nogil&type=any)

=== "Homebrew"

    On macOS and Linux, you can use Homebrew:

    ```bash
    brew install python-freethreading
    ```

    This will install the interpreter at `$(brew --prefix)/bin/python3.13t`.

    On macOS, the Python framework built with the free-threading ABI can be found at `$(brew --prefix)/Frameworks/PythonT.framework`.

## Installing a Jupyter Kernel

While Jupyter [does not currently support free-threaded
Python](https://github.com/jupyterlab/jupyterlab/issues/16915), you can use
Jupyter with a regular build of Python and a free-threaded Jupyter kernel. To do
so, install the kernel to a location that is visible to both Python
installations:

```bash
python3.13t -m ipykernel install --name python3.13t --user
```

And then you should be able to launch new jupyterlab or jupyter notebook
sessions using the `python3.13t` kernel to experiment with free-threaded Python.

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
pyenv install --debug --keep 3.13.1
```

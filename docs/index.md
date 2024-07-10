---
description: py-free-threading is a centralized collection of documentation and trackers around compatibility with free-threaded CPython for the Python open source ecosystem
---

# Introduction

Free-threaded CPython is coming! :material-language-python: :thread:

After the [acceptance by the Python Steering Council](https://discuss.python.org/t/a-steering-council-notice-about-pep-703-making-the-global-interpreter-lock-optional-in-cpython/30474)
of, and the [gradual rollout strategy](https://discuss.python.org/t/pep-703-making-the-global-interpreter-lock-optional-in-cpython-acceptance/37075) for,
[PEP 703 - Making the Global Interpreter Lock Optional in CPython](https://peps.python.org/pep-0703/),
a lot of work is happening both in CPython itself and across the Python ecosystem.

This website aims to serve as a centralized resource both for Python package
maintainers and end users interested in supporting or experimenting with
free-threaded Python. An overview of the compatibility status of various Python
libraries is maintained in:

- [Compatibility status tracking](tracking.md)

This website also provide documentation and porting guidance - with a focus on
extension modules using the Python C API, because that's where most of the work
will be. The following resources should get you started:

- [Installing free-threaded CPython](installing_cpython.md)
- [Running Python with the GIL disabled](running-gil-disabled.md)
- [Porting extension modules to support free-threading](porting.md)
- [Setting up CI](ci.md)



## About this site

Any contributions are very much welcome - please open issues or pull requests
[on this repo](https://github.com/Quansight-Labs/free-threaded-compatibility)
for anything that seems in scope for this site or for tracking issues related
to support for free-threaded Python across the ecosystem.

This site is maintained primarily by Quansight Labs, where a team is working
together with the Python runtime team at Meta and stakeholders across the
ecosystem to jumpstart work on converting the libraries that make up the
scientific Python and AI/ML stacks to work with the free-threaded build of
CPython 3.13. Additionally, that effort will look at libraries like PyO3 that
are needed to interface with CPython from other languages.


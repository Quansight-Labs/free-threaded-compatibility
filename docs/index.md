---
description: pyfreethreading is a centralized collection of documentation and trackers around compatibility with the free-threaded build of CPython in the PyData ecosystem
---

## Introduction

Quansight Labs is working with the Python runtime team at Meta and stakeholders
across the ecosystem to jumpstart work on converting the libraries that make up
the scientific Python and AI/ML stacks to work with the free-threaded (nogil)
build of CPython 3.13. Additionally, we will look at libraries like PyO3
that are needed to interface with CPython from other languages.

Our initial goal is to ensure libraries at the bottom of the stack like
NumPy, pybind11, and Cython are usable with free-threaded CPython. We will also
be updating packaging tools like meson-python needed to support building wheels
for free-threaded CPython. Once those tools and libraries are in a stable
enough state, we will begin looking at libraries higher in the stack.

This website aims to serve as a centralized resource both for Python C extension
authors and Python users.

We aim to provide documentation and porting guidance to extension authors
with the following resources:

- [Building free-threaded CPython](building.md)
- [Running Python with the GIL disabled](running-gil-disabled.md)
- [Porting extension modules to support free-threading](porting.md)
- [Guide to Continuous Integration](ci.md)

Python users will be able to view the compatibility status of various
Python libraries with the free-threaded build:

- [Compatibility status tracking](tracking.md)

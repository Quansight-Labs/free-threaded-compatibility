## Improving Ecosystem Compatibility with Free-Threaded Python

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

### What is this repository?

This repository is for coordinating ecosystem-wide work. We will use
this repository to track, understand, and provide documentation for
dealing with issues that we find are common across many
libraries. Issues that are specific to a project should be reported in
that project's issue tracker.

### Documentation

You can find documentation for various free-threading topics
[on our site](https://pyfreethreading.github.io).

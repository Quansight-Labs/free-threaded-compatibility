# Contributing

We very much welcome ideas, questions and relevant contributions from anyone
with an interest in improving the adoption and usage of free-threaded CPython.

Please read the Code of Conduct in the root of the repository and be mindful of
the community rules while working on the project.

## Contributing to this site

Contributions can be made through issues on and pull requests to the
[free-threaded-compatibility](https://github.com/Quansight-Labs/free-threaded-compatibility)
repository. Ways to contribute include:

- Improvements to the documentation, from new content to copy-editing for clarity.
- Updates to the [status tracker](https://py-free-threading.github.io/tracking/).
- Adding links to relevant examples, blog posts and other content.
- For particularly exciting use cases or benchmarks, including them directly
    into the site instead of only linking out to them.

## Contributing to the adoption of free-threading

There's a ton of work to do here - and a ton of fun and performance to be had!
This is perhaps the single most impactful and exciting change to CPython since
the Python 2 to Python 3 transition. It's going to take the community multiple
years to complete the transition to free-threaded CPython, and your help will
be valuable. Here are some ways to contribute today:

1. Start experimenting! If the packages you rely on for some task or application,
    try running it with a free-threaded interpreter. And consider whether it can
    benefit performance or functionality-wise from Python-level threading.
1. Implement support for free-threading in packages that are still lacking
    support. We'll try to provide an outline of how to approach that in an open
    source package below.

### Implementing support for free-threading in a package

A good place to start is to check the current status of the package. Are there
docs on free-threading support? Does the issue tracker for the package have an
issue about adding free-threading support? If not, is there a relevant PR?
Typically, searching for "free-threading", "free-threaded", "GIL", "3.13t" and
"cp313t" will allow you to find the relevant issue or PR if it exists.

If there is no issue yet and you want to contribute support, opening an issue
is usually a good next step (please check the projects contribution guidelines
for details on how the maintainers want you to suggest a new feature). Here
is example content for such an issue:

```markdown
Title: *Support for free-threaded CPython*

I am interested in adding support for free-threading to PROJECT-NAME. I had a
look at what it would take to implement that.

<!-- INSERT YOUR THOUGHTS SPECIFIC TO THE PACKAGE HERE:
- Are there relevant threading-related issues or docs?
- If there are native libraries (C, C++, etc.), are they thread-safe? Does code
  in the package already drop the GIL?
- Is there relevant global state?
- Are there particular parts of the code base for which dedicated
  multi-threaded tests should be written?
-->

The standard TODOs for adding free-threading support are:

- [ ] Audit Python bindings and declare them free-threading compatible (xref https://py-free-threading.github.io/porting/#updating-extension-modules).
- [ ] Run the test suite with `pytest-run-parallel` to find potential issues, and fix them.
- [ ] Run the test suite under ThreadSanitizer. _If possible, depends on how many dependencies there are and if they run under TSan._
- [ ] Add `cp313t-*` to CI to build free-threading wheels.

For more details, please see the
[suggested plan of attack in the py-free-threading guide](https://py-free-threading.github.io/porting/#suggested-plan-of-attack).

Note that this is the first time I've looked at this repo, so I might be
missing known issues or code that needs closer inspection. Any suggestions here
will be very useful.

I will be happy to help and work on this. Please do let me know if you'd prefer
me to hold off for any reason.
```

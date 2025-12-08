# More Resources

Apart from this website, there's a wide list of resources on the
free-threaded build and free-threading topics in general, including
documentation, blog posts, conference talks, and others. We'll
try to keep an up-to-date list here:

## CPython documentation

- [Python experimental support for free threading](https://docs.python.org/3/howto/free-threading-python.html#freethreading-python-howto)
- [C API Extension Support for Free Threading HOWTO on docs.python.org](https://docs.python.org/3/howto/free-threading-extensions.html)

## Free-threading pre-history and background

- [PEP 703 design document](https://docs.google.com/document/d/18CXhDb1ygxg-YXNBJNzfzZsDFosB5e6BfnXLlejd9l0/edit?usp=sharing)
- [PEP 703 initial discussion thread](https://discuss.python.org/t/22606), as
    well as the [follow-up discussion thread](https://discuss.python.org/t/26503)
- [PEP 703 acceptance announcement](https://discuss.python.org/t/37075)

## Community-maintained packages

- [`ft_utils` documentation](https://facebookincubator.github.io/ft_utils/)
- [`cereggii`](https://github.com/dpdani/cereggii)

## Conference talks

### PyData Seattle 2025

- ["Unlocking Parallel PyTorch Inference (and More!) with Python Free-Threading" by Trent Nelson](https://www.youtube.com/watch?v=9PFcG9MZ3s8)
    - Direct link to [deck](https://trent.me/decks/pytorch-and-python-free-threading/#/title-slide)
    - Based on the article [PyTorch and Python Free-Threading](https://trent.me/articles/pytorch-and-python-free-threading/)

### EuroPython 2025

- ["Parallel programming and Cython" by David Woods](https://youtu.be/7azKz3YP7eA)

### PyCon 2025

- ["Unraveling Community Support for Free-Threaded Python" by Lysandros Nikoloau and Nathan Goldbaum](https://youtu.be/EuU3ksI1l04)
- ["High-Performance Python: Faster Type Checking and Free Threaded Execution" by Sam Gross and Neil Mitchell](https://youtu.be/ZTSZ1OCUaeQ)
- ["Using Rust in Free-Threaded vs Regular Python 3.13" by David Hewitt](https://youtu.be/J7phN_M4GLM)
- ["Building a NoGIL Load Balancer in 30 minutes" by Alvaro Duran](https://youtu.be/AYSlsCz8gKM)

### EuroPython 2022

- ["Keynote: Multithreaded Python without the GIL"](https://www.youtube.com/watch?v=9OOJcTp8dqE)

## Community blog posts

- [Simon Willison's post about trying out free-threaded Python on macOS](https://til.simonwillison.net/python/trying-free-threaded-python)
- [Codspeed's blog post about free-threading performance](https://codspeed.io/blog/state-of-python-3-13-performance-free-threading)
- [NVIDIA's blog post about threaded data loading](https://developer.nvidia.com/blog/improved-data-loading-with-threads/)
- [Quansight Labs blog post about start of work on free-threading](https://labs.quansight.org/blog/free-threaded-python-rollout)
- [Quansight Labs blog post about one year of work on free-threading](https://labs.quansight.org/blog/free-threaded-one-year-recap)

## CPython internals

There's also a lot of useful resources on CPython internals, that are not
specific to the free-threaded build:

- [CPython internal docs](https://github.com/python/cpython/tree/main/InternalDocs)
- [Dated tutorial on writing C extension modules](https://llllllllll.github.io/c-extension-tutorial/)
- [Python behind the scenes series](https://tenthousandmeters.com/tag/python-behind-the-scenes/)
- [Łukasz Langa's PyCon Thailand talk on the Python 3.13 release](https://www.youtube.com/watch?v=uL_kmagVKFQ)
- [Anthony Shaw's PyCon US talk on free-threading and other parallelism concepts](https://www.youtube.com/watch?v=Mp5wKOL4L2Q)

# Examples Demonstrating Free-Threaded Python

This page gathers examples showing how to use free-threaded Python to speed up
code using the Python `threading` module. In all cases, the free-threaded build outperforms the GIL-enabled build since the GIL-enabled build does not
scale well due to lock contention.

- [Mandelbrot Set Visualization](mandelbrot.md)
- [Monte Carlo Simulation](monte-carlo.md)
- [Web Scraping with asyncio](asyncio.md)

External examples:

- [Benchmarking a web service on the free-threaded build](https://blog.baro.dev/p/the-future-of-python-web-services-looks-gil-free)
- [Improved Data Loading on GPUs with Threads](https://developer.nvidia.com/blog/improved-data-loading-with-threads/)
- [Using `AtomicDict.reduce()` for Multithreaded Aggregation](https://dpdani.github.io/cereggii/examples/AtomicDict/reduce/)

We'd love to have more examples! See [the contribution guide](../contributing.md)
if you're interested in adding more use-cases that show off the free-threaded
build.

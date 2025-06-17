# Examples Demonstrating Free-Threaded Python

This page gathers examples showing how to use free-threaded Python to speed up
code using the Python `threading` module. In all cases, the examples do not
scale well on the GIL-enabled build due to lock contention.

- [Mandelbrot Set Visualization](mandelbrot.md)
- [Monte Carlo Simulation](monte-carlo.md)
- [Web Scraping with asyncio](asyncio.md)

We'd love to have more examples! See [the contribution guide](../contributing.md)
if you're interested in adding more use-cases that show off the free-threaded
build.
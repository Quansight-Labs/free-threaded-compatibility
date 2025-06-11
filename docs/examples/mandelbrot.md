# Mandelbrot Set Visualization

!!! note

    See [the worked example notebook accompanying this page](mandelbrot-threads.ipynb)

The [Mandelbrot set](https://en.wikipedia.org/wiki/Mandelbrot_set) is a classic
example of a [fractal](https://en.wikipedia.org/wiki/Fractal) - a mathematical
structure with lots of inherent complexity that can be fun to
visualize.

One way to compute a visualization of the set requires looping over coordinates
in the complex plane corresponding to the centers of pixels in an image. Whether
or not a point in the complex plane is in the mandelbrot set is a function only
of the point's coordinates, so visualizing the set is very amenable to parallel
speedups by breaking up the work into chunks of pixels.

Algorithms to visualize the set range in complexity and sophistication. Here is
a very basic version that calculates whether a given complex number, `z = x +
y*1j`, is in the mandelbrot set. The function returns 0 for points inside the
set and returns the number of iterations executed for points outside the set:

```python
def mandelbrot(x, y, max_iterations=500):
    z = complex(0, 0)
    p = 2
    c = complex(x, y)
    for iteration_number in range(max_iterations):
        if abs(z) >= 2:
            return iteration_number
        else:
            z = z**p + c
    else:
        return 0
```

We can create an image of the Mandelbrot set by creating an array of pixels and
assigning x and y coordinates to the center of each pixel. We can then loop over
the array and call the mandelbrot function for each pixel. Let's make use of a
2D NumPy array to represent the image:

```python
import numpy as np

shape = (1000, 1000)

iteration_array = np.zeros(shape)
for (i, x) in enumerate(x_domain):
    for (j, y) in enumerate(y_domain):
        iteration_array[j, i] = mandelbrot(x, y)
```

This sort of ["map-reduce"](https://en.wikipedia.org/wiki/MapReduce) workflow,
where a problem reduces to looping over a batch of calculations, is particularly
amenable to parallel computation. On free-threaded Python, we can transform the
simple single-threaded for loop above into a multithreaded parallel loop by
making use of a worker function that processes a chunk of pixels:

```python
def worker(j_y):
    for (i, x) in enumerate(x_domain):
        for (j, y) in j_y:
            iteration_array[j, i] = mandelbrot(x, y)
```

This function can be called by a `concurrent.futures.ThreadPoolExecutor` and
operate on a chunk of columns in the image:

```python
def run_thread_pool(num_workers):
    with ThreadPoolExecutor(max_workers=num_workers) as tpe:
        chunks = itertools.batched(enumerate(y_domain), 4, strict=True)
        futures = [tpe.submit(worker, arg) for arg in chunks]
        # block until all work finishes
        concurrent.futures.wait(futures) 
```

In [the notebook accompanying this page](mandelbrot-threads.ipynb) you can see
how executing `run_thread_pool` scales well as a function of the number of
worker threads up to 32 threads, the number of CPU cores available on the test
machine.

The parallel throughput of a mandelbrot visualization algorithm is limited by
how much CPU power can be used to compute whether or not a point is in the
set. This is an example of a "CPU-bound" task. Since the algorithm is
implemented as a Python function that doesn't call into any libraries that
release the GIL, the GIL prevents parallel execution of the `mandelbrot`
function on the GIL-enabled build, and you will not see any parallel speedups
running the example notebook using the GIL-enabled interpreter.
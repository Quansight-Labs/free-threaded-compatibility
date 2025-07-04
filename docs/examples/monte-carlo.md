# Multithreaded Monte Carlo Simulation

Modern computer programs that play the game of Go commonly use Monte Carlo Tree
Search (MCTS) as the search algorithm. Examples of programs using this
technique are AlphaGo, CrazyStone and Zen. Look for "AlphaGo - The Movie" on
YouTube if you are interested in a story about how AlphaGo won a 5 game match
verses a professional Go player. Monte Carlo-based algorithms are typically
good candidates for multi-threaded or multi-process parallelization.

Michi is a minimal but relatively full-featured Go engine that uses MCTS. It
was authored by Petr Baudis and released under the MIT license. We will use it
as an example of how free-threaded Python can speed up programs that use
multiple threads. In the case of Michi, parallelizing the computation using
multiple processes also works well.

## Run the example

1. To get a copy of the program, clone the following GitHub repository: https://github.com/nascheme/michi.git

1. To run the program using multiple threads and with the GIL, use the following
    command line:

    ```
    uv run --python=3.14 python michi.py --force-threads tsbenchmark
    ```

1. To run with free-threaded Python, run the following command:

    ```
    uv run --python=3.14t python michi.py --force-threads tsbenchmark
    ```

## Understanding the results

On an AMD Ryzen 5 7600X 6-core processor, the following performance is obtained:

| Configuration                | Time [s] |
| ---------------------------- | -------- |
| default build, threads       | 50.5     |
| default build, processes     | 4.7      |
| free-threaded build, threads | 4.8      |

These results show that if a problem is well-suited for multi-process parallelization,
it can be the most efficient approach. In the case of Michi, the inter-process
communication required consists of sending positions to the worker processes
and retrieving the position evaluation. This data is small and easily
marshalled.

As expected, the multi-threaded approach with the GIL enabled has poor
performance. Because the program's work is almost entirely CPU-bound, the GIL
prevents multi-threading from providing any significant speed-up.

Looking at the free-threaded build, it has a small amount of overhead
compared with the multi-process approach. There are two main factors that
cause this. First, the free-threaded build is generally a bit slower overall
than the default build. Typically, it is about 90 to 95% of the speed,
depending on the platform and program. Secondly, there is likely some
contention between the threads when the Go program is running, where multiple
threads are trying to use the same resource concurrently. The multi-process
approach does not have this kind of contention overhead.

Depending on the program, it can be simple to start utilizing multiple threads.
In the case of Michi, the following change was all that was required. In other
programs, additional changes may be required to prevent data races. An
additional optimization was made to make each thread use its own random
generator state.

```
  -        worker_pool = Pool(processes=n_workers)
  +        if FORCE_THREADS or not sys._is_gil_enabled():
  +            print(f'using thread pool, n = {n_workers}')
  +            worker_pool = ThreadPool(processes=n_workers)
  +        else:
  +            print(f'using process pool, n = {n_workers}')
  +            worker_pool = Pool(processes=n_workers)
```

This example demonstrates that if your problem involves a significant amount of
CPU-bound calculation, Python's GIL renders multi-threading an ineffective
solution. With free-threaded Python, performance when using multiple threads is
comparable to a multi-process solution. In summary, if data sharing between
multiple processes is not practical or efficient, free-threaded Python could be
an excellent tool for unlocking the performance of multi-core CPUs.

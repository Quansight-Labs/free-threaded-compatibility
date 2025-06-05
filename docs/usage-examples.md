# Examples Demonstrating Free-Threaded Python

This page gather examples showing how to use free-threaded Python to speed up
code using the Python `threading` module. In all cases, the examples do not
scale well on the GIL-enabled build due to lock contention.

## Parallel processing of shared NumPy arrays.

## Multithreaded Monte Carlo Simulation

## Asyncio TCP proxy
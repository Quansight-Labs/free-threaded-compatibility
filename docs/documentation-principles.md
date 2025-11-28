# Documentation Principles

This document outlines principles and guidelines for documenting free-threading in
CPython core documentation and the broader Python ecosystem. These principles aim
to provide clear, accurate, and maintainable documentation while avoiding common
pitfalls.

## Core Principles

These principles apply to both CPython core documentation and ecosystem documentation.

### 1. Document Reality, Not Aspirations

Only document features, behaviors, and guarantees that are actually implemented and
tested. Documentation should reflect the current state, not planned features.

- Don't document future aspirations as parts of the current feature set or design
- Don't document incomplete work unless it causes crashes or data corruption
- If partially implemented, clearly state what works and what doesn't
- Use issue trackers and PEPs for planned features, not user-facing docs

Good: "Individual operations on `x` are atomic. Sequences of operations require
external synchronization for deterministic results."

Bad: "The `x` type will be fully thread-safe in a future release."

### 2. Centralize Thread Safety Documentation

Prefer centralized documentation over scattered thread-safety notes. Thread safety
concerns cut across many APIs; centralizing makes documentation consistent,
comprehensive, and easier to maintain.

- Create dedicated pages for thread safety guarantees (by type, by module)
- Link to centralized docs from specific API entries when needed
- Use module-level notes for most Python APIs, not per-function notes
- For C APIs, use hybrid approach: centralized overview plus inline notes for
    critical APIs

Good: Centralized "Thread Safety of Built-in Types" page with per-type guarantees,
linked from individual type docs.

Bad: Scattered thread safety notes on every method without consistent structure.

### 3. Balance Detail with Succinctness

Provide enough detail for users to write correct code without overwhelming them
with implementation details.

- Focus on guarantees needed to write correct code
- Link to PEPs and other resources for implementation details
- Use examples to illustrate complex concepts
- Python APIs: module-level summaries, not per-API notes
- C APIs: more detail since extension authors need lower-level understanding

Good: "Individual list operations like `append()` and `pop()` are atomic. Compound
operations require external synchronization. See PEP 703 for implementation details."

Bad (too brief): "Thread-safe."

Bad (too detailed): "The list implementation uses biased critical sections. Each
operation acquires locks in the following order..."

### 4. Distinguish Levels of Support

Clearly differentiate between different levels of thread safety. Not all code needs
to be fully thread-safe; clear distinctions help users understand guarantees.

- Use consistent terminology (see [Terminology](#free-threading-terminology))
- Document known limitations explicitly
- Use trove classifiers for package-level support declarations

Good: "Individual `x` operations are atomic and will not cause crashes. Sequences
of operations may observe inconsistent state without external synchronization.
Iteration while another thread modifies the `x` may raise RuntimeError."

Bad: "Thread-safe." (no indication of what this means or limitations)

### 5. Be Consistent Across Documentation

Use consistent terminology, structure, and level of detail across all free-threading
documentation. Consistency helps users build accurate mental models.

- Use terms defined in [Terminology](#free-threading-terminology)
- Follow the same structure for similar content
- Cross-reference related documentation
- Use the same examples and idioms across guides

Good: All docs for different types follow same structure.

### 6. Document Critical Issues

Even if something is a bug or incomplete work, document it if it's likely to cause
serious problems. Users need to know about critical issues to avoid crashes, data
corruption, or security problems.

- Document known issues that cause crashes or data corruption
- Warn about common pitfalls leading to subtle bugs
- Provide workarounds when available
- Link to issue tracker for status
- Remove or update warnings once resolved

### 7. Provide Actionable Guidance

Documentation should help users know what to do, not just what exists. Users need
to understand not just how things work, but how to use them correctly.

- Include examples of correct usage
- Show common patterns and idioms
- Explain when synchronization is needed
- Provide migration guides for porting existing code
- Link to tools and testing strategies

Good: Code example showing lock usage for compound operations on `x`, explicitly
noting that individual reads don't require the lock.

Bad: "The `x` type provides atomic operations for basic access." (no guidance on how to
use safely)

## Anti-Patterns to Avoid

### Vague Statements

Bad: "Most operations are thread-safe."

Good: "Individual `append()` and `pop()` operations are atomic. Compound operations require synchronization."

### Implementation Details in User Docs

Bad: "The GIL is replaced by biased reference counting with deferred RC for..."

Good: "Free-threaded Python removes the GIL, enabling parallel execution. See PEP 703
for implementation details."

### Scattered Thread Safety Notes

Bad: Thread safety mentioned inconsistently across 50 different function docs.

Good: Centralized thread safety page with links from individual functions.

## Examples of Good Documentation

### Example 1: Built-in Type Thread Safety

````md
# Thread Safety of Built-in Types

## MyDict

### Guarantees

- **Individual operations are atomic**: Operations like `d[key]`, `d.get(key)`,
  `d[key] = value`, and `d.pop(key)` execute atomically and will not cause crashes
  or corruption.

- **Object invariants maintained**: Internal data structures remain consistent
  even under concurrent access.

### Limitations

- **Compound operations require synchronization**: Sequences like "check if key
  exists, then insert" may observe inconsistent state:

  ```python
  # Not deterministic without external lock
  if key not in d:
      d[key] = value  # Another thread might have added key
  ```

- **Iteration not thread-safe during modification**: Iterating over a `MyDict` instance
    while another thread modifies it may raise `RuntimeError` or produce inconsistent
    results.

### Recommended Patterns

For compound operations:

```python
from threading import Lock

lock = Lock()
with lock:
    if key not in d:
        d[key] = value
```

For iteration over possibly-modified dict:

```python
# Option 1: Snapshot
for key, value in dict(d).items():
    process(key, value)

# Option 2: External lock
with lock:
    for key, value in d.items():
        process(key, value)
```

````

## Free-Threading Terminology

This section provides definitions of key terms for describing the thread-safety guarantees
of Python library APIs. Library maintainers should use these terms when documenting how
their APIs can be used from multiple threads.

### Thread-Safety Guarantee Levels

When documenting your library's APIs, use these numbered levels to describe their
concurrent access guarantees:

#### 1. Immutable

An object whose state cannot be modified after creation. Immutable objects can be safely
shared across threads without synchronization.

When to use: For objects that provide no mutating operations.

Example: "Configuration objects are immutable once created and can be safely shared
across all threads."

#### 2. Isolated / Thread-Local

An API where each thread has its own independent instance or state. No cross-thread
sharing occurs.

When to use: When your library maintains per-thread state.

Example: "Each thread gets its own random number generator state. Operations are
isolated and require no synchronization."

#### 3. Atomic

An operation that completes as a single, indivisible unit from the perspective of other
threads. No other thread can observe a partial state.

When to use: For operations that either complete fully or not at all, with no
observable intermediate state.

Example: "The `increment()` method is atomic - other threads will see either the old
or new value, never a partial update."

Note: Atomic operations may still have race conditions when combined with other
operations. Atomicity only guarantees the operation itself is indivisible.

#### 4. Internally Synchronized

An API that uses internal locking or synchronization mechanisms. Multiple threads can
call the API concurrently without external coordination.

When to use: When your library handles all necessary locking internally.

Example: "The connection pool is internally synchronized. Multiple threads can safely
call `acquire()` and `release()` concurrently."

#### 5. Linearizable

Operations that appear to execute atomically at some point between their start and
completion, with results consistent with some sequential order.

When to use: For operations that provide strong consistency guarantees.

Example: "Queue operations are linearizable - `get()` returns items in the order
they were `put()`, even across threads."

#### 6. Externally Synchronized

An API that requires callers to provide their own synchronization (e.g., locks) when
used from multiple threads concurrently.

When to use: When thread-safety is the caller's responsibility.

Example: "The parser requires external synchronization. Protect calls with a lock
when sharing a parser instance across threads."

#### 7. Reentrant

An API that can safely be called again before a previous invocation has completed,
including from signal handlers.

When to use: Important for signal handlers and callbacks.

Example: "This function is reentrant and safe to call from signal handlers."

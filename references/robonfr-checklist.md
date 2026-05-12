# RoboNFR Detailed Checklist

Reference document for the four NFR review dimensions. Load this when the user wants deep, systematic evaluation rather than a quick scan.

## Table of Contents

1. [Code Design](#1-code-design)
2. [Readability](#2-readability)
3. [Reliability](#3-reliability)
4. [Performance](#4-performance)

---

## 1. Code Design

### 1.1 Single Responsibility Principle (SRP)
- [ ] Each class/module has one reason to change
- [ ] Each function performs one clear task
- [ ] File length is under the baseline limit (see nfr-baseline-templates.md)

### 1.2 Coupling & Cohesion
- [ ] Imports are limited to what is necessary
- [ ] No circular dependencies
- [ ] Related functions/data are grouped in the same module
- [ ] Law of Demeter: objects only talk to immediate friends

### 1.3 Extensibility
- [ ] New features can be added without modifying existing code (Open/Closed)
- [ ] Interfaces are used to allow swapping implementations
- [ ] Configuration is externalized, not hard-coded

### 1.4 Abstraction Level
- [ ] Public APIs hide implementation details
- [ ] No leakage of internal data structures
- [ ] Consistent abstraction level within a function (no mixing high-level orchestration with low-level bit manipulation)

### 1.5 Design Patterns & Anti-Patterns
- [ ] Patterns are used where they simplify, not complicate
- [ ] No God Objects
- [ ] No Feature Envy (a method that uses more data from another class than its own)

### 1.6 Technical Debt
- [ ] No TODO/FIXME without a ticket reference
- [ ] No commented-out code blocks
- [ ] Dead code is removed, not left behind

---

## 2. Readability

### 2.1 Naming
- [ ] Variable names reveal intent (not `data`, `tmp`, `x`)
- [ ] Function names are verb-led (`calculateTotal`, not `total`)
- [ ] Boolean variables are phrased as predicates (`isValid`, `hasPermission`)
- [ ] Constants are ALL_CAPS or namespaced

### 2.2 Comments & Documentation
- [ ] "Why" is commented, not "What" (the code shows what)
- [ ] Public APIs have docstrings / JSDoc / GoDoc
- [ ] Complex algorithms reference the source paper or URL
- [ ] Comments are current (not describing deleted logic)

### 2.3 Formatting & Style
- [ ] Consistent indentation and brace style
- [ ] Vertical whitespace separates logical steps
- [ ] Line length under 100-120 characters
- [ ] No trailing whitespace

### 2.4 Complexity
- [ ] Cyclomatic complexity ≤ 10 per function (ideally ≤ 5)
- [ ] Cognitive complexity is low (minimal nesting)
- [ ] Each function fits on one screen (~50 lines)

### 2.5 Magic Numbers / Strings
- [ ] All literals are extracted to named constants
- [ ] Timeouts, buffer sizes, and limits are configurable

### 2.6 Code Smells
- [ ] No duplicated code (DRY)
- [ ] No long parameter lists (>4 suggests a struct/object)
- [ ] No shotgun surgery (one change requires edits in many places)

---

## 3. Reliability

### 3.1 Error Handling
- [ ] All errors are handled, not swallowed
- [ ] Errors return context (file, operation, original error)
- [ ] Panic/exit is reserved for unrecoverable startup failures only
- [ ] Graceful degradation is implemented where possible

### 3.2 Input Validation
- [ ] All external inputs are validated (user, file, network, env)
- [ ] Validation happens at the system boundary
- [ ] Type safety is enforced (structs over maps where possible)

### 3.3 Resource Management
- [ ] Files and connections are closed (defer/try-with-resources/context managers)
- [ ] Memory allocations are bounded (no unbounded slices/lists)
- [ ] Timeouts are set on all network and DB operations

### 3.4 Concurrency Safety
- [ ] Shared mutable state is minimized
- [ ] Mutexes/RWMutexes protect shared data
- [ ] No data races (use race detector / ThreadSanitizer)
- [ ] Goroutines / threads have cancellation support (context.Context, stop channels)

### 3.5 Testing
- [ ] Critical paths have unit tests
- [ ] Error branches are tested, not just happy paths
- [ ] Integration tests cover I/O boundaries
- [ ] Tests are deterministic (no flaky sleeps or random data without seeding)

### 3.6 Idempotency & Safety
- [ ] Operations are safe to retry (idempotent where needed)
- [ ] Duplicate requests do not corrupt state
- [ ] Migrations and deployments are backward-compatible

---

## 4. Performance

### 4.1 Algorithmic Complexity
- [ ] Time complexity is appropriate for input size
- [ ] No hidden O(n²) loops inside ostensibly linear code
- [ ] Sorting/searching uses standard library optimized implementations

### 4.2 Resource Usage
- [ ] No memory leaks (circular references, forgotten event listeners)
- [ ] Large allocations are pooled or reused
- [ ] Object creation in hot loops is minimized

### 4.3 Database Efficiency
- [ ] No N+1 queries
- [ ] Indexes exist for queried columns
- [ ] Transactions are as short as possible
- [ ] Pagination is used for large result sets

### 4.4 Laziness & Caching
- [ ] Expensive computations are deferred until needed
- [ ] Repeated lookups are cached (with TTL or invalidation)
- [ ] No premature optimization, but no obvious pessimization either

### 4.5 Scalability
- [ ] Statelessness is preferred for horizontally scalable services
- [ ] No single-threaded global bottlenecks
- [ ] Backpressure is handled (rate limiting, queue limits)

### 4.6 I/O Efficiency
- [ ] Batch operations are used where possible
- [ ] Streaming is used for large payloads
- [ ] Compression is enabled for network transfers

# NFR Baseline Templates

Technology-specific baselines for NFR thresholds. Use these to calibrate what "good" looks like per stack.

## Table of Contents

1. [Python](#1-python)
2. [JavaScript / TypeScript](#2-javascript--typescript)
3. [Go](#3-go)
4. [Rust](#4-rust)
5. [Java](#5-java)
6. [Generic / Polyglot](#6-generic--polyglot)

---

## 1. Python

### Complexity

| Metric | Warning | Block |
|--------|---------|-------|
| Cyclomatic Complexity | > 10 | > 15 |
| Function Length | > 50 lines | > 100 lines |
| Class Length | > 300 lines | > 500 lines |
| File Length | > 500 lines | > 1000 lines |
| Method Args | > 5 | > 7 |

### Performance

| Metric | Warning | Block |
|--------|---------|-------|
| DB Queries per Request | > 5 | > 10 |
| List Comprehension Depth | > 2 nested | > 3 nested |
| Regex in Hot Path | Review | Block if uncompiled |

### Tools
- **Primary:** Pylint, Ruff, Bandit
- **Complexity:** Radon (`radon cc -a`)
- **Security:** Bandit
- **Type Safety:** mypy

### Example `.pylintrc` Snippet

```ini
[DESIGN]
max-args=5
max-locals=15
max-returns=6
max-branches=12
max-statements=50
```

---

## 2. JavaScript / TypeScript

### Complexity

| Metric | Warning | Block |
|--------|---------|-------|
| Cyclomatic Complexity | > 10 | > 15 |
| Function Length | > 40 lines | > 80 lines |
| File Length | > 400 lines | > 800 lines |
| Nested Callbacks | > 3 | > 5 |
| Class Methods | > 15 | > 25 |

### Performance

| Metric | Warning | Block |
|--------|---------|-------|
| Bundle Size (entry) | > 250KB | > 500KB |
| setState in Loop | Review | Block |
| Memory Leaks (listeners) | Review | Block if unbounded |

### Tools
- **Primary:** ESLint, typescript-eslint
- **Complexity:** eslint-plugin-complexity
- **Security:** eslint-plugin-security
- **Import:** eslint-plugin-import (circular dep detection)

### Example `.eslintrc` Snippet

```json
{
  "rules": {
    "complexity": ["warn", 10],
    "max-lines-per-function": ["warn", 50],
    "max-params": ["warn", 4]
  }
}
```

---

## 3. Go

### Complexity

| Metric | Warning | Block |
|--------|---------|-------|
| Cyclomatic Complexity | > 10 | > 15 |
| Function Length | > 50 lines | > 100 lines |
| File Length | > 500 lines | > 1000 lines |
| Interface Methods | > 10 | > 15 |
| Package Files | > 15 | > 30 |

### Performance

| Metric | Warning | Block |
|--------|---------|-------|
| goroutine Leaks | Review | Block |
| Unbuffered Channels in Loop | Review | Block |
| `interface{}` Usage | Review | Block in hot path |

### Tools
- **Primary:** `go vet`, `golint` (or `revive`), `staticcheck`
- **Complexity:** `gocyclo`
- **Security:** `gosec`
- **Format:** `gofmt`, `goimports`

### Example Makefile Snippet

```makefile
lint:
	gofmt -d .
	go vet ./...
	staticcheck ./...
	gocyclo -over 10 .
	gosec ./...
```

---

## 4. Rust

### Complexity

| Metric | Warning | Block |
|--------|---------|-------|
| Cyclomatic Complexity | > 10 | > 15 |
| Function Length | > 50 lines | > 100 lines |
| Match Arms | > 10 | > 20 |
| Generic Parameters | > 3 | > 5 |

### Performance

| Metric | Warning | Block |
|--------|---------|-------|
| `clone()` in Loop | Review | Block in hot path |
| `unwrap()` / `expect()` | Review | Block in library code |
| `Vec` Pre-allocation | Suggest `with_capacity` | — |

### Tools
- **Primary:** `clippy`, `rustfmt`
- **Complexity:** `cargo-cyclonedx` (indirect), `rust-code-analysis`
- **Security:** `cargo-audit`

### Example `clippy` Invocation

```bash
cargo clippy -- -W clippy::complexity \
              -W clippy::perf \
              -D clippy::unwrap_used
```

---

## 5. Java

### Complexity

| Metric | Warning | Block |
|--------|---------|-------|
| Cyclomatic Complexity | > 10 | > 15 |
| Method Length | > 50 lines | > 100 lines |
| Class Length | > 400 lines | > 800 lines |
| Method Args | > 5 | > 7 |
| Class Fields | > 15 | > 25 |

### Performance

| Metric | Warning | Block |
|--------|---------|-------|
| Stream Chains > 10 ops | Review | — |
| String Concat in Loop | Replace with StringBuilder | — |
| Synchronized on Mutable | Review | Block |

### Tools
- **Primary:** Checkstyle, SpotBugs, PMD
- **Complexity:** PMD (`CyclomaticComplexity` rule)
- **Security:** SpotBugs + FindSecBugs plugin
- **Format:** google-java-format

---

## 6. Generic / Polyglot

When reviewing multi-language repos or architecture-level changes:

| Concern | Guideline |
|---------|-----------|
| Service Boundary | Each service owns its data; no shared DB schemas |
| API Latency | P99 < 200ms (internal), P99 < 500ms (external) |
| Error Rate | < 0.1% for 2xx endpoints |
| Test Coverage | Critical paths ≥ 70%, overall ≥ 50% |
| Documentation | Every public API has OpenAPI / Protobuf spec |
| Secrets | No secrets in repo; use secret manager or env injection |
| Logging | Structured JSON; no PII in logs; correlation IDs propagated |
| Observability | RED metrics (Rate, Errors, Duration) for all services |

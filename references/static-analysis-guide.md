# Static Analysis Tool Guide

Reference for configuring and interpreting static analysis tools alongside NFR reviews.

## Table of Contents

1. [SonarQube Community Edition](#1-sonarqube-community-edition)
2. [Semgrep](#2-semgrep)
3. [CodeQL](#3-codeql)
4. [Pylint](#4-pylint)
5. [Quick-Start CI Templates](#6-quick-start-ci-templates)

---

## 1. SonarQube Community Edition

**Best for:** Team-wide quality gates, technical debt tracking, trend dashboards.

### Key Rules for NFR Reviews

| Rule Category | Examples | NFR Dimension |
|---------------|----------|---------------|
| Code Smells | Cognitive Complexity, Duplicated Blocks | Readability, Design |
| Reliability | Null pointer dereference, Resource leak | Reliability |
| Maintainability | Too many parameters, Long method | Design, Readability |
| Security (Hotspots) | Hard-coded credentials, SQL injection | Reliability |

### Recommended Quality Gate

```properties
# Minimum viable quality gate for NFR focus
coverage >= 60%
duplicated_lines_density <= 3%
cognitive_complexity <= 15 per function
blocker_violations = 0
critical_violations = 0
```

### Integration

```bash
# Local scan before PR
sonar-scanner \
  -Dsonar.projectKey=my-project \
  -Dsonar.sources=. \
  -Dsonar.host.url=http://localhost:9000 \
  -Dsonar.token=$SONAR_TOKEN
```

---

## 2. Semgrep

**Best for:** Fast feedback, custom project-specific rules, security scanning.

### Recommended Rulesets

| Ruleset | Purpose |
|---------|---------|
| `p/default` | General best practices |
| `p/cwe-top-25` | Security vulnerabilities |
| `p/owasp-mobile` | Mobile-specific issues |
| `p/python` / `p/javascript` | Language-specific idioms |

### Custom NFR Rules

Create `.semgrep/nfr-rules.yml`:

```yaml
rules:
  - id: no-unbounded-arrays
    pattern: |
      $ARR = []
      ...
      while ...:
        $ARR.append(...)
    message: "Potential unbounded memory growth. Add size limits."
    languages: [python]
    severity: WARNING
    metadata:
      nfr_dimension: Performance

  - id: no-raw-sql-in-loop
    pattern: |
      for ...:
        ...
        execute($SQL)
    message: "Possible N+1 query. Consider batching or JOIN."
    languages: [python, javascript, go]
    severity: WARNING
    metadata:
      nfr_dimension: Performance
```

### Run

```bash
semgrep --config=auto --config=.semgrep/nfr-rules.yml --error .
```

---

## 3. CodeQL

**Best for:** Deep semantic analysis, security-critical codebases, GitHub-native integration.

### Key NFR Queries

| Query | Description | Dimension |
|-------|-------------|-----------|
| `py/unclear-exception-handling` | Bare except clauses | Reliability |
| `go/unhandled-error` | Ignored error returns | Reliability |
| `js/useless-assignment` | Dead stores | Readability |
| `java/missing-override-annotation` | Missing `@Override` | Readability |
| `cpp/missing-return` | Missing return statements | Reliability |

### GitHub Actions Integration

```yaml
- name: Initialize CodeQL
  uses: github/codeql-action/init@v3
  with:
    languages: python, javascript
    queries: security-extended,security-and-quality

- name: Autobuild
  uses: github/codeql-action/autobuild@v3

- name: Perform CodeQL Analysis
  uses: github/codeql-action/analyze@v3
```

---

## 4. Pylint

**Best for:** Python-specific complexity, style, and code smell detection.

### NFR-Focused Configuration

`.pylintrc`:

```ini
[MASTER]
load-plugins=pylint.extensions.mccabe

[DESIGN]
max-args=5
max-locals=15
max-returns=6
max-branches=12
max-statements=50
max-parents=7
max-attributes=7

[MESSAGES CONTROL]
disable=C0114,C0115,C0116  ; re-enable if docstring coverage is required
enable=R0911,R0912,R0913,R0914,R0915,W0104  ; complexity & dead code

[REPORTS]
output-format=colorized
reports=no
score=yes
```

### Key Metrics Mapping

| Pylint Code | Meaning | NFR Dimension |
|-------------|---------|---------------|
| R0911 | Too many return statements | Readability |
| R0912 | Too many branches | Readability, Design |
| R0913 | Too many arguments | Design |
| R0914 | Too many local variables | Readability |
| R0915 | Too many statements | Readability |
| W0104 | Pointless statement | Reliability |
| W0613 | Unused argument | Readability |

---

## 5. Quick-Start CI Templates

### GitHub Actions (Multi-tool)

```yaml
name: NFR Static Analysis
on: [pull_request]
jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Semgrep
        uses: returntocorp/semgrep-action@v1
        with:
          config: >-
            p/default
            p/cwe-top-25
      - name: SonarQube Scan
        uses: SonarSource/sonarqube-scan-action@v5
        env:
          SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
      - name: Pylint (Python)
        if: hashFiles('**/*.py') != ''
        run: |
          pip install pylint
          pylint --fail-under=8.0 $(git ls-files '*.py')
```

### Pre-commit Hook

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pycqa/pylint
    rev: v3.2.0
    hooks:
      - id: pylint
        args: ['--fail-under=8.0']
  - repo: https://github.com/returntocorp/semgrep
    rev: v1.0.0
    hooks:
      - id: semgrep
        args: ['--config=auto', '--error']
```

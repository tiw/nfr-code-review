---
name: nfr-code-review
argument-hint: "<file-or-directory> or <paste-code>"
allowed-tools: Read, Grep, Glob, Bash
description: |
  Non-Functional Requirements (NFR) code review based on the RoboNFR framework.
  Evaluates code across four dimensions: Code Design, Readability, Reliability, and Performance.
  Combines LLM-driven qualitative analysis with static analysis tool recommendations
  (SonarQube, Semgrep, CodeQL, Pylint) for objective metrics.
  Use when asked to "NFR review", "non-functional code review", "code quality review",
  "review readability", "review reliability", "review performance", "review code design",
  "RoboNFR review", "review Python quality", "review JavaScript quality", "review Go performance",
  or when the user wants to assess code against non-functional requirements
  rather than functional correctness.
  NOT for functional bug hunting, syntax linting, or security penetration testing.
---

# NFR Code Review Skill

Review code changes through the lens of Non-Functional Requirements (NFR), following the systematic RoboNFR evaluation framework.

## Review Philosophy

NFR reviews complement functional reviews. They answer:
- Is the code maintainable and understandable?
- Will it perform under load?
- Is it resilient to failures?
- Does the architecture support future growth?

Best practice: Combine this qualitative LLM review with static analysis tools for objective metrics (cyclomatic complexity, coupling, duplication).

## Four Review Dimensions

Evaluate every change across these four dimensions. Score each as: ✅ Pass / ⚠️ Concern / ❌ Block.

### 1. Code Design

Assess architectural and structural quality:
- **Single Responsibility**: Does each module/class/function have one clear purpose?
- **Coupling & Cohesion**: Are dependencies minimized? Are related elements grouped?
- **Extensibility**: Can new features be added without modifying existing code (Open/Closed)?
- **Abstraction Level**: Are interfaces clean and implementation details hidden?
- **Design Patterns**: Are appropriate patterns used (not over-engineered)?
- **Tech Debt**: Does the change introduce or reduce technical debt?

### 2. Readability

Assess how quickly another developer can understand the code:
- **Naming**: Are variables, functions, classes named with clear intent?
- **Comments & Documentation**: Are complex sections explained? Are comments current?
- **Formatting & Style**: Is the code consistently formatted and visually scannable?
- **Complexity**: Can each function be understood in under 30 seconds? (check cyclomatic complexity)
- **Magic Numbers/Strings**: Are literals extracted to named constants?
- **Code Smells**: Any duplicated code, long methods, or large classes?

### 3. Reliability

Assess robustness and error handling:
- **Error Handling**: Are edge cases and failures handled gracefully?
- **Input Validation**: Are inputs sanitized and validated at boundaries?
- **Resource Management**: Are resources (files, connections, memory) properly released?
- **Concurrency Safety**: Are shared resources protected in multi-threaded contexts?
- **Testing Coverage**: Are critical paths covered by unit/integration tests?
- **Idempotency**: Are operations safe to retry?

### 4. Performance

Assess efficiency and scalability:
- **Algorithmic Complexity**: Is the chosen algorithm appropriate for the data volume?
- **Resource Usage**: Memory, CPU, I/O — any obvious bottlenecks?
- **Database Efficiency**: N+1 queries, missing indexes, unnecessary transactions?
- **Lazy vs Eager**: Is expensive work deferred until needed?
- **Scalability**: Will this pattern hold as data/user count grows?
- **Caching Opportunities**: Are repeated expensive computations cached?

## Review Workflow

1. **Scope Definition**: Identify which files/changes are in scope. If the user has not provided a target, ask for a file path or pasted code. Exclude generated files, vendored dependencies, and test data. If no files remain after exclusion, report this clearly and ask the user to refine the scope.
2. **Static Analysis Check**: Recommend running relevant tools and incorporating their output:
   - **SonarQube CE**: Quality gates, technical debt, code smells (21+ languages)
   - **Semgrep**: Fast pattern-based scanning for custom rules
   - **CodeQL**: Semantic analysis, 39 built-in maintainability queries
   - **Pylint**: Cyclomatic complexity, code smells (Python)
3. **Dimension Evaluation**: Walk through each of the four dimensions above with specific evidence from the code.
4. **Severity Classification**:
   - **Block**: Must fix before merge (security risk, data loss, severe performance degradation)
   - **Concern**: Should fix in this PR or very soon (maintainability issue, missing error handling)
   - **Suggestion**: Nice to have (naming improvement, minor optimization, style)
5. **Structured Report**: Output findings in the format below.

## Output Format

```markdown
## NFR Code Review Report

### Summary
- **Files Reviewed**: N
- **Overall Score**: X/4 (count of ✅ dimensions)
- **Blockers**: N | **Concerns**: N | **Suggestions**: N

### Dimension Scores

#### 1. Code Design — ✅/⚠️/❌
[Evidence with file:line references]

#### 2. Readability — ✅/⚠️/❌
[Evidence with file:line references]

#### 3. Reliability — ✅/⚠️/❌
[Evidence with file:line references]

#### 4. Performance — ✅/⚠️/❌
[Evidence with file:line references]

### Static Analysis Recommendations
[Which tools to run and what to look for]

### Action Items
| Priority | Item | File:Line | Dimension |
|----------|------|-----------|-----------|
| Block | ... | ... | ... |
| Concern | ... | ... | ... |
| Suggestion | ... | ... | ... |

### Positive Highlights
[What is done well — reinforce good practices]
```

### Example Report (Abbreviated)

```markdown
## NFR Code Review Report

### Summary
- **Files Reviewed**: 2
- **Overall Score**: 3/4
- **Blockers**: 0 | **Concerns**: 1 | **Suggestions**: 1

### Dimension Scores

#### 1. Code Design — ✅
Clean separation between data parsing and report rendering.

#### 2. Readability — ⚠️
`utils.py:42` Function `process_data` is 78 lines long (exceeds 50-line warning threshold). Consider extracting helper functions.

#### 3. Reliability — ✅
Graceful handling of missing JSON keys in `parse-sonar-report.py:55`.

#### 4. Performance — ✅
No obvious bottlenecks for current data volumes.

### Action Items
| Priority | Item | File:Line | Dimension |
|----------|------|-----------|-----------|
| Concern | Function exceeds 50 lines | utils.py:42 | Readability |
| Suggestion | Add type hints to public functions | utils.py:42 | Readability |
```

## Bundled Resources

Load these references when the user asks for deeper detail, specific language guidance, or CI setup help:

- **Detailed checklists**: Read [`references/robonfr-checklist.md`](references/robonfr-checklist.md) when the user wants a line-by-line audit or a printable checklist.
- **Static analysis setup**: Read [`references/static-analysis-guide.md`](references/static-analysis-guide.md) when configuring SonarQube, Semgrep, CodeQL, or CI pipelines.
- **Language baselines**: Read [`references/nfr-baseline-templates.md`](references/nfr-baseline-templates.md) when reviewing Python, JavaScript/TypeScript, Go, Rust, or Java codebases.

Run bundled scripts when automation is needed:

- **Complexity scan**: `scripts/complexity-check.sh [path]` — cross-language function length and cyclomatic complexity scan (falls back to embedded Python if `lizard` is unavailable).
- **SonarQube parse**: `scripts/parse-sonar-report.py --input issues.json` — converts SonarQube JSON output into an NFR-aligned Markdown summary.
- **Report generation**: `scripts/generate-report.py --input data.json --output report.md` — renders a structured JSON review into the standard Markdown report format.

## Progressive Adoption Roadmap

For teams introducing NFR reviews:

1. **Week 1-2**: Use this skill for manual review on critical PRs. Focus on Readability and Reliability (highest impact, lowest friction).
2. **Week 3-4**: Add SonarQube or Semgrep to CI for objective metrics on Code Design and Performance.
3. **Month 2**: Establish internal NFR baselines per team using [`references/nfr-baseline-templates.md`](references/nfr-baseline-templates.md).
4. **Month 3+**: Integrate NFR checks into IDE pre-commit hooks and PR templates for automatic interception.

## Reference Tools

When reviewing, suggest the right tool for the finding:

| Tool | Best For | When to Suggest |
|------|----------|-----------------|
| SonarQube CE | Overall quality gates, tech debt tracking | Team-wide CI integration |
| Semgrep | Custom security/style rules, fast feedback | Adding project-specific rules |
| CodeQL | Deep semantic analysis, vulnerability hunting | Security-critical codebases |
| Pylint | Python complexity, style enforcement | Python projects without ruff/black |

## Notes

- Always cite specific file paths and line numbers.
- Balance criticism with positive highlights — mention what the author did well.
- If business context is needed (e.g., "is this performance optimization necessary?"), flag for human review rather than guessing.
- For generated code (LLM output), apply the same NFR standards — generated code often has subtle reliability and performance issues.

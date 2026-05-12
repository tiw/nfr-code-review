# NFR Code Review

Non-Functional Requirements (NFR) code review skill based on the **RoboNFR** framework. Evaluates code across four dimensions — **Code Design**, **Readability**, **Reliability**, and **Performance** — combining LLM-driven qualitative analysis with static analysis tool recommendations.

Inspired by research on open-source LLM code review tools (PR-Agent, Tabby, Kodus AI) and the RoboNFR academic framework for systematic NFR evaluation.

---

## Overview

This skill helps reviewers assess code changes through the lens of non-functional quality rather than functional correctness alone. It provides:

- **Four-dimension evaluation** with clear ✅/⚠️/❌ scoring
- **Structured report format** with file-line evidence and actionable items
- **Static analysis integration** (SonarQube, Semgrep, CodeQL, Pylint)
- **Language-specific baselines** for Python, JavaScript/TypeScript, Go, Rust, and Java
- **Automation scripts** for complexity scanning and report generation

---

## Repository Structure

```
nfr-code-review/
├── SKILL.md                              # Core skill definition for AI agents
├── README.md                             # This file
├── references/
│   ├── robonfr-checklist.md              # Detailed per-dimension checklists
│   ├── static-analysis-guide.md          # Tool configuration & CI templates
│   └── nfr-baseline-templates.md         # Language-specific thresholds
└── scripts/
    ├── parse-sonar-report.py             # Convert SonarQube JSON → NFR summary
    ├── complexity-check.sh               # Cross-language complexity scanner
    └── generate-report.py                # Structured JSON → Markdown report
```

---

## Quick Start

### As an AI Agent Skill

Place this directory in your skills path:

- `~/.config/agents/skills/`
- `~/.kimi/skills/`
- `~/.claude/skills/`
- `.agents/skills/` (project-level)

Trigger phrases:
- `NFR review`
- `non-functional code review`
- `code quality review`
- `review readability / reliability / performance`
- `RoboNFR review`

### Standalone Scripts

**Complexity check:**
```bash
./scripts/complexity-check.sh src/
# or with lizard (if installed):
./scripts/complexity-check.sh --lizard src/
```

**Parse SonarQube report:**
```bash
python3 scripts/parse-sonar-report.py \
  --input sonar-issues.json \
  --format markdown
```

**Generate report from JSON:**
```bash
python3 scripts/generate-report.py \
  --input review-data.json \
  --output report.md
```

---

## Four Review Dimensions

### 1. Code Design
Single Responsibility, coupling & cohesion, extensibility, abstraction level, design patterns, technical debt.

### 2. Readability
Naming, comments & documentation, formatting, complexity (cyclomatic & cognitive), magic numbers, code smells.

### 3. Reliability
Error handling, input validation, resource management, concurrency safety, test coverage, idempotency.

### 4. Performance
Algorithmic complexity, resource usage, database efficiency, laziness & caching, scalability, I/O efficiency.

See [`references/robonfr-checklist.md`](references/robonfr-checklist.md) for the full itemized checklist.

---

## Static Analysis Integration

| Tool | Best For | NFR Dimensions |
|------|----------|----------------|
| [SonarQube CE](references/static-analysis-guide.md#1-sonarqube-community-edition) | Quality gates, tech debt tracking | Design, Readability, Reliability |
| [Semgrep](references/static-analysis-guide.md#2-semgrep) | Fast feedback, custom rules | All |
| [CodeQL](references/static-analysis-guide.md#3-codeql) | Semantic analysis, security | Reliability, Design |
| [Pylint](references/static-analysis-guide.md#4-pylint) | Python complexity & style | Readability, Design |

See [`references/static-analysis-guide.md`](references/static-analysis-guide.md) for configuration examples and CI templates.

---

## Language Baselines

Per-technology thresholds for complexity, file length, and performance:

- [Python](references/nfr-baseline-templates.md#1-python)
- [JavaScript / TypeScript](references/nfr-baseline-templates.md#2-javascript--typescript)
- [Go](references/nfr-baseline-templates.md#3-go)
- [Rust](references/nfr-baseline-templates.md#4-rust)
- [Java](references/nfr-baseline-templates.md#5-java)
- [Generic / Polyglot](references/nfr-baseline-templates.md#6-generic--polyglot)

---

## Progressive Adoption

1. **Week 1–2**: Manual NFR review on critical PRs (focus on Readability + Reliability)
2. **Week 3–4**: Add SonarQube or Semgrep to CI for objective metrics
3. **Month 2**: Establish internal NFR baselines per team/stack
4. **Month 3+**: Integrate checks into IDE pre-commit hooks and PR templates

---

## Contributing

This is a living skill. To extend:

- **New language baselines**: Add a section to `references/nfr-baseline-templates.md`
- **New static analysis rules**: Add to `references/static-analysis-guide.md`
- **New automation scripts**: Drop into `scripts/` and update this README

---

## License

MIT

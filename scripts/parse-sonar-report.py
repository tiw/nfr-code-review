#!/usr/bin/env python3
"""
Parse SonarQube scanner or Web API JSON output and produce an NFR-aligned summary.

Usage:
    python parse_sonar_report.py --input sonar-report.json [--format markdown|json]

Supports:
    - SonarQube Web API /api/issues/search response
    - SonarScanner generic-issue JSON (if exported)
"""

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path


def load_report(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def map_severity(sonar_severity: str) -> str:
    mapping = {
        "BLOCKER": "Block",
        "CRITICAL": "Block",
        "MAJOR": "Concern",
        "MINOR": "Suggestion",
        "INFO": "Suggestion",
    }
    return mapping.get(sonar_severity.upper(), "Concern")


def map_dimension(rule_key: str, message: str) -> str:
    """Heuristic mapping from Sonar rule/message to NFR dimension."""
    rk = rule_key.lower()
    msg = message.lower()

    reliability_rules = [
        "null", "exception", "error", "resource leak", "thread", "race",
        "injection", "security", "vulnerability", "xss", "sql",
    ]
    performance_rules = [
        "performance", "n+1", "inefficient", "slow", "memory", "buffer",
        "concatenation", "loop",
    ]
    readability_rules = [
        "complexity", "cognitive", "naming", "format", "comment",
        "duplication", "dead", "unused",
    ]

    for token in reliability_rules:
        if token in rk or token in msg:
            return "Reliability"
    for token in performance_rules:
        if token in rk or token in msg:
            return "Performance"
    for token in readability_rules:
        if token in rk or token in msg:
            return "Readability"

    return "Code Design"


def extract_issues(data: dict) -> list:
    """Normalize both /api/issues/search and scanner JSON shapes."""
    if "issues" in data:
        return data["issues"]
    if "components" in data and "issues" not in data:
        # Some export formats nest differently; fallback to issues list at root
        return data.get("issues", [])
    return []


def summarize(issues: list) -> dict:
    summary = {
        "total": len(issues),
        "by_severity": defaultdict(int),
        "by_dimension": defaultdict(lambda: defaultdict(int)),
        "files": defaultdict(lambda: defaultdict(int)),
    }

    for issue in issues:
        severity = map_severity(issue.get("severity", "MAJOR"))
        dimension = map_dimension(
            issue.get("rule", ""),
            issue.get("message", ""),
        )
        file_path = issue.get("component", issue.get("filePath", "unknown"))

        summary["by_severity"][severity] += 1
        summary["by_dimension"][dimension][severity] += 1
        summary["files"][file_path][severity] += 1

    return summary


def to_markdown(summary: dict, issues: list) -> str:
    lines = []
    lines.append("## SonarQube NFR Summary")
    lines.append("")
    lines.append(f"- **Total Issues**: {summary['total']}")
    lines.append(f"- **Block**: {summary['by_severity'].get('Block', 0)}")
    lines.append(f"- **Concern**: {summary['by_severity'].get('Concern', 0)}")
    lines.append(f"- **Suggestion**: {summary['by_severity'].get('Suggestion', 0)}")
    lines.append("")

    lines.append("### By Dimension")
    lines.append("")
    lines.append("| Dimension | Block | Concern | Suggestion |")
    lines.append("|-----------|-------|---------|------------|")
    for dim in ("Code Design", "Readability", "Reliability", "Performance"):
        counts = summary["by_dimension"].get(dim, {})
        lines.append(
            f"| {dim} | {counts.get('Block', 0)} | {counts.get('Concern', 0)} | {counts.get('Suggestion', 0)} |"
        )
    lines.append("")

    lines.append("### Top Files")
    lines.append("")
    lines.append("| File | Block | Concern | Suggestion |")
    lines.append("|------|-------|---------|------------|")
    sorted_files = sorted(
        summary["files"].items(),
        key=lambda x: x[1].get("Block", 0) * 100 + x[1].get("Concern", 0),
        reverse=True,
    )[:10]
    for file_path, counts in sorted_files:
        lines.append(
            f"| {file_path} | {counts.get('Block', 0)} | {counts.get('Concern', 0)} | {counts.get('Suggestion', 0)} |"
        )
    lines.append("")

    lines.append("### Detailed Issues")
    lines.append("")
    for issue in issues[:50]:  # cap to avoid huge output
        severity = map_severity(issue.get("severity", "MAJOR"))
        dimension = map_dimension(issue.get("rule", ""), issue.get("message", ""))
        file_path = issue.get("component", issue.get("filePath", "unknown"))
        line = issue.get("line", "—")
        message = issue.get("message", "").replace("|", "\\|")
        lines.append(
            f"- **[{severity}]** [{dimension}] `{file_path}:{line}` — {message}"
        )
    if len(issues) > 50:
        lines.append(f"\n... and {len(issues) - 50} more issues.")

    return "\n".join(lines)


def to_json(summary: dict) -> str:
    # Convert defaultdicts to plain dicts for JSON serialization
    clean = {
        "total": summary["total"],
        "by_severity": dict(summary["by_severity"]),
        "by_dimension": {k: dict(v) for k, v in summary["by_dimension"].items()},
        "files": {k: dict(v) for k, v in summary["files"].items()},
    }
    return json.dumps(clean, indent=2, ensure_ascii=False)


def main():
    parser = argparse.ArgumentParser(description="Parse SonarQube report for NFR review")
    parser.add_argument("--input", "-i", required=True, help="Path to SonarQube JSON report")
    parser.add_argument("--format", "-f", choices=["markdown", "json"], default="markdown")
    args = parser.parse_args()

    if not Path(args.input).exists():
        print(f"Error: File not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    data = load_report(args.input)
    issues = extract_issues(data)
    summary = summarize(issues)

    if args.format == "markdown":
        print(to_markdown(summary, issues))
    else:
        print(to_json(summary))


if __name__ == "__main__":
    main()

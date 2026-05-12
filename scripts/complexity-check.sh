#!/usr/bin/env bash
#
# Cross-language complexity and size check.
# Falls back to embedded Python if lizard is not installed.
#
# Usage:
#   ./complexity-check.sh [path]
#   ./complexity-check.sh --lizard [path]   # force lizard mode
#
# Exit codes:
#   0 = all metrics pass baseline
#   1 = one or more metrics exceed block thresholds

set -euo pipefail

TARGET_PATH="${1:-.}"
USE_LIZARD=false

if [[ "${1:-}" == "--lizard" ]]; then
    USE_LIZARD=true
    TARGET_PATH="${2:-.}"
fi

# Thresholds
WARN_CCN=10
BLOCK_CCN=15
WARN_LINES=50
BLOCK_LINES=100
WARN_FILE=500
BLOCK_FILE=1000

run_lizard() {
    if ! command -v lizard &>/dev/null; then
        echo "lizard not found. Install: pip install lizard"
        return 1
    fi

    echo "Running lizard on $TARGET_PATH ..."
    lizard \
        --CCN_warn "$WARN_CCN" \
        --length_warn "$WARN_LINES" \
        --arguments 5 \
        "$TARGET_PATH"
}

run_embedded() {
    echo "Running embedded complexity scan on $TARGET_PATH ..."
    python3 - "$TARGET_PATH" "$WARN_CCN" "$BLOCK_CCN" "$WARN_LINES" "$BLOCK_LINES" "$WARN_FILE" "$BLOCK_FILE" <<'PYEOF'
import ast
import os
import re
import sys
from pathlib import Path

target = sys.argv[1]
WARN_CCN = int(sys.argv[2])
BLOCK_CCN = int(sys.argv[3])
WARN_LINES = int(sys.argv[4])
BLOCK_LINES = int(sys.argv[5])
WARN_FILE = int(sys.argv[6])
BLOCK_FILE = int(sys.argv[7])

block_count = 0

LANG_PATTERNS = {
    ".py": r"^\s*def\s+|^\s*async\s+def\s+",
    ".js": r"^\s*(async\s+)?function\s+|\b\w+\s*[:=]\s*(async\s*)?\(",
    ".ts": r"^\s*(async\s+)?function\s+|\b\w+\s*[:=]\s*(async\s*)?\(",
    ".go": r"^\s*func\s+",
    ".java": r"^\s*(public|private|protected|static|\s)+[\w\<\>\[\]]+\s+(\w+)\s*\(",
    ".rs": r"^\s*(pub\s+)?fn\s+",
}

def count_cyclomatic(lines):
    """Naïve CCN: count branching keywords."""
    branches = re.compile(
        r"\b(if|elif|else|for|while|except|catch|case|default|\?\:|\|\||&&)\b"
    )
    return 1 + sum(branches.search(line) is not None for line in lines)

def scan_file(path: Path):
    global block_count
    ext = path.suffix
    if ext not in LANG_PATTERNS:
        return

    func_pattern = re.compile(LANG_PATTERNS[ext])
    content = path.read_text(encoding="utf-8", errors="ignore")
    lines = content.splitlines()
    file_len = len(lines)

    # File-level check
    if file_len > BLOCK_FILE:
        print(f"[BLOCK] {path}: file length {file_len} > {BLOCK_FILE}")
        block_count += 1
    elif file_len > WARN_FILE:
        print(f"[WARN]  {path}: file length {file_len} > {WARN_FILE}")

    # Function-level scan
    in_func = False
    func_start = 0
    brace_depth = 0

    for i, line in enumerate(lines):
        stripped = line.strip()

        # Simple brace counting for C-style languages
        if ext in (".js", ".ts", ".go", ".java", ".rs"):
            if func_pattern.search(line):
                in_func = True
                func_start = i
                brace_depth = 0

            if in_func:
                brace_depth += stripped.count("{") - stripped.count("}")
                if brace_depth <= 0 and "{" in line or "}" in line:
                    func_len = i - func_start + 1
                    func_lines = lines[func_start:i+1]
                    ccn = count_cyclomatic(func_lines)
                    report_func(path, func_start + 1, func_len, ccn)
                    in_func = False
        else:
            # Python: indentation-based
            if func_pattern.search(line):
                if in_func:
                    # report previous
                    func_len = i - func_start
                    func_lines = lines[func_start:i]
                    ccn = count_cyclomatic(func_lines)
                    report_func(path, func_start + 1, func_len, ccn)
                in_func = True
                func_start = i

    if in_func and ext == ".py":
        func_len = len(lines) - func_start
        func_lines = lines[func_start:]
        ccn = count_cyclomatic(func_lines)
        report_func(path, func_start + 1, func_len, ccn)

def report_func(path, start_line, length, ccn):
    global block_count
    if ccn > BLOCK_CCN:
        print(f"[BLOCK] {path}:{start_line} CCN={ccn} (>{BLOCK_CCN}), len={length}")
        block_count += 1
    elif ccn > WARN_CCN:
        print(f"[WARN]  {path}:{start_line} CCN={ccn} (>{WARN_CCN}), len={length}")
    elif length > BLOCK_LINES:
        print(f"[BLOCK] {path}:{start_line} len={length} (>{BLOCK_LINES}), CCN={ccn}")
        block_count += 1
    elif length > WARN_LINES:
        print(f"[WARN]  {path}:{start_line} len={length} (>{WARN_LINES}), CCN={ccn}")

for root, _, files in os.walk(target):
    for fname in files:
        fpath = Path(root) / fname
        if fpath.suffix in LANG_PATTERNS:
            scan_file(fpath)

sys.exit(1 if block_count > 0 else 0)
PYEOF
}

# Main
if $USE_LIZARD; then
    run_lizard
else
    if command -v lizard &>/dev/null; then
        run_lizard
    else
        run_embedded
    fi
fi

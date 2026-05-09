#!/usr/bin/env python3
"""
Batch syntax checker for all languages used in the codebase.

Usage:
    python3 compile_check.py [file-or-dir ...]

Detects language by file extension and runs the appropriate check.
If no args given, auto-detects the project root from CWD and scans.

Exit code: 0 if all pass, 1 if any fail.
"""

import subprocess
import sys
import os
from pathlib import Path

CHECKERS = {
    ".py":  ["python3", "-c", "import py_compile, sys; sys.exit(py_compile.compile('{path}', doraise=True) is None)"],
    ".js":  ["node", "-c", "{path}"],
    ".ts":  ["npx", "--no-install", "tsc", "--noEmit", "--strict", "{path}"],
    ".jsx": ["npx", "--no-install", "tsc", "--noEmit", "--strict", "--jsx", "preserve", "{path}"],
    ".tsx": ["npx", "--no-install", "tsc", "--noEmit", "--strict", "--jsx", "preserve", "{path}"],
    ".sh":  ["bash", "-n", "{path}"],
    ".rb":  ["ruby", "-c", "{path}"],
    ".go":  ["gofmt", "-e", "{path}"],
    ".rs":  ["rustc", "--check", "{path}"],
    ".java": ["javac", "-proc:none", "{path}"],
    ".yaml": ["python3", "-c", "import yaml, sys; yaml.safe_load(open('{path}')); print('yaml OK')"],
    ".yml":  ["python3", "-c", "import yaml, sys; yaml.safe_load(open('{path}')); print('yaml OK')"],
    ".json": ["python3", "-c", "import json, sys; json.load(open('{path}')); print('json OK')"],
    ".toml": ["python3", "-c", "import tomllib, sys; tomllib.load(open('{path}')); print('toml OK')"],
}

# Extensions that should be checked with project-level tooling instead
PROJECT_CHECK = {
    ".ts":  "npx tsc --noEmit --strict",
    ".tsx": "npx tsc --noEmit --strict",
}

def check_file(path: str) -> bool:
    ext = Path(path).suffix
    if ext not in CHECKERS:
        return True  # skip unknown

    cmd = [part.format(path=path) for part in CHECKERS[ext]]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    if result.returncode != 0:
        print(f"FAIL {path}")
        for line in result.stderr.strip().split("\n")[-10:]:
            print(f"  {line}")
        return False
    else:
        print(f"OK   {path}")
        return True

def find_changed_files(paths: list[str]) -> list[str]:
    """If no paths given, scan git-tracked changed files."""
    if paths:
        return paths

    # Check if we're in a git repo
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", "--diff-filter=ACM"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0 and result.stdout.strip():
            return [f for f in result.stdout.strip().split("\n") if os.path.isfile(f)]

        # Also check unstaged changes
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0 and result.stdout.strip():
            return [f for f in result.stdout.strip().split("\n") if os.path.isfile(f)]
    except FileNotFoundError:
        pass

    # No git repo, scan common source dirs
    src_dirs = ["src", "lib", "app", "."]
    files = []
    for d in src_dirs:
        p = Path(d)
        if p.is_dir():
            for ext in CHECKERS:
                files.extend(str(f) for f in p.rglob(f"*{ext}"))
    return files

def main():
    files = find_changed_files(sys.argv[1:])

    if not files:
        print("No files to check.")
        sys.exit(0)

    print(f"Checking {len(files)} files...")
    failed = 0
    for f in files:
        if not check_file(f):
            failed += 1

    total = len(files)
    if failed:
        print(f"{total} files checked. {failed} FAILED.")
        sys.exit(1)
    else:
        print(f"{total} files checked. All OK.")

if __name__ == "__main__":
    main()

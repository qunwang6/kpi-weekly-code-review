#!/usr/bin/env python3
"""Collect weekly git evidence for KPI performance review."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path


GENERATED_HINTS = (
    "package-lock.json",
    "pnpm-lock.yaml",
    "yarn.lock",
    "Cargo.lock",
    "Podfile.lock",
    ".min.js",
    ".snap",
    "dist/",
    "build/",
    "generated/",
    "vendor/",
)


def run_git(args: list[str], cwd: Path, check: bool = True) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if check and result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "git command failed")
    return result.stdout.strip()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Collect weekly git evidence for KPI review.")
    parser.add_argument("--days", type=int, default=7, help="Lookback window in days. Default: 7.")
    parser.add_argument("--since", help="Explicit git --since value, e.g. '2026-05-08'.")
    parser.add_argument("--author", help="Filter commits by git author.")
    parser.add_argument("--base", help="Optional base branch/ref for diff summary.")
    parser.add_argument("--json", action="store_true", help="Emit JSON only.")
    return parser.parse_args()


def git_root(cwd: Path) -> Path:
    root = run_git(["rev-parse", "--show-toplevel"], cwd)
    return Path(root)


def split_records(raw: str) -> list[dict[str, str]]:
    records: list[dict[str, str]] = []
    for block in [b for b in raw.split("\x1e") if b.strip()]:
        fields = block.strip("\n").split("\x1f")
        if len(fields) >= 5:
            records.append(
                {
                    "hash": fields[0],
                    "author": fields[1],
                    "email": fields[2],
                    "date": fields[3],
                    "subject": fields[4],
                }
            )
    return records


def collect_commits(root: Path, since: str, author: str | None) -> list[dict[str, str]]:
    pretty = "%x1e%h%x1f%an%x1f%ae%x1f%ad%x1f%s"
    args = ["log", f"--since={since}", f"--pretty=format:{pretty}", "--date=short"]
    if author:
        args.insert(1, f"--author={author}")
    raw = run_git(args, root, check=False)
    return split_records(raw)


def collect_numstat(root: Path, since: str, author: str | None, base: str | None) -> list[dict[str, object]]:
    if base:
        args = ["diff", "--numstat", f"{base}...HEAD"]
    else:
        args = ["log", f"--since={since}", "--numstat", "--pretty=format:"]
        if author:
            args.insert(1, f"--author={author}")
    raw = run_git(args, root, check=False)
    rows: list[dict[str, object]] = []
    for line in raw.splitlines():
        parts = line.split("\t")
        if len(parts) != 3:
            continue
        added_s, deleted_s, path = parts
        added = 0 if added_s == "-" else int(added_s)
        deleted = 0 if deleted_s == "-" else int(deleted_s)
        generated = any(hint in path for hint in GENERATED_HINTS)
        rows.append({"path": path, "added": added, "deleted": deleted, "generated_or_lock": generated})
    return rows


def detect_quality_commands(root: Path) -> list[str]:
    commands: list[str] = []
    package_json = root / "package.json"
    if package_json.exists():
        try:
            data = json.loads(package_json.read_text())
            scripts = data.get("scripts", {})
            for name in ("test", "lint", "typecheck", "check"):
                if name in scripts:
                    commands.append(f"npm run {name}" if name != "test" else "npm test")
        except json.JSONDecodeError:
            commands.append("package.json exists but could not be parsed")
    if (root / "pyproject.toml").exists() or (root / "pytest.ini").exists():
        commands.append("pytest")
        commands.append("ruff check .")
    if (root / "Cargo.toml").exists():
        commands.append("cargo test")
        commands.append("cargo clippy")
    if (root / "go.mod").exists():
        commands.append("go test ./...")
    return commands


def summarize(commits: list[dict[str, str]], rows: list[dict[str, object]]) -> dict[str, object]:
    authors = Counter(c["author"] for c in commits)
    extensions = Counter(Path(str(r["path"])).suffix or "[none]" for r in rows)
    touched = Counter(str(r["path"]) for r in rows)
    totals = {
        "files_changed": len(touched),
        "lines_added": sum(int(r["added"]) for r in rows),
        "lines_deleted": sum(int(r["deleted"]) for r in rows),
        "generated_or_lock_files": sum(1 for r in rows if r["generated_or_lock"]),
    }
    non_generated = [r for r in rows if not r["generated_or_lock"]]
    totals["non_generated_lines_changed"] = sum(int(r["added"]) + int(r["deleted"]) for r in non_generated)
    return {
        "commit_count": len(commits),
        "authors": authors.most_common(),
        "totals": totals,
        "top_changed_files": touched.most_common(15),
        "extensions": extensions.most_common(12),
    }


def render_markdown(payload: dict[str, object]) -> str:
    lines = [
        "# Weekly KPI Evidence",
        "",
        f"- Repository: `{payload['repository']}`",
        f"- Window: `{payload['window']}`",
        f"- Base diff: `{payload.get('base') or 'not used'}`",
        f"- Author filter: `{payload.get('author') or 'all authors'}`",
        "",
        "## Summary",
    ]
    summary = payload["summary"]
    assert isinstance(summary, dict)
    totals = summary["totals"]
    assert isinstance(totals, dict)
    lines.extend(
        [
            f"- Commits: {summary['commit_count']}",
            f"- Files changed: {totals['files_changed']}",
            f"- Lines added/deleted: +{totals['lines_added']} / -{totals['lines_deleted']}",
            f"- Non-generated lines changed: {totals['non_generated_lines_changed']}",
            f"- Generated/lock files touched: {totals['generated_or_lock_files']}",
            "",
            "## Authors",
        ]
    )
    for author, count in summary["authors"]:
        lines.append(f"- {author}: {count} commit(s)")
    lines.extend(["", "## Recent Commits"])
    for commit in payload["commits"][:30]:
        lines.append(f"- `{commit['hash']}` {commit['date']} {commit['author']}: {commit['subject']}")
    lines.extend(["", "## Top Changed Files"])
    for path, count in summary["top_changed_files"]:
        lines.append(f"- `{path}`: {count} change record(s)")
    lines.extend(["", "## Suggested Quality Commands"])
    commands = payload["quality_commands"]
    if commands:
        for command in commands:
            lines.append(f"- `{command}`")
    else:
        lines.append("- No common project quality commands detected. Inspect repo docs/config manually.")
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    try:
        root = git_root(Path.cwd())
        since = args.since or (datetime.now(timezone.utc) - timedelta(days=args.days)).date().isoformat()
        commits = collect_commits(root, since, args.author)
        rows = collect_numstat(root, since, args.author, args.base)
        payload = {
            "repository": str(root),
            "window": f"since {since}",
            "author": args.author,
            "base": args.base,
            "summary": summarize(commits, rows),
            "commits": commits,
            "quality_commands": detect_quality_commands(root),
        }
        if args.json:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            print(render_markdown(payload))
        return 0
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml>=6"]
# ///
"""Validate an OKF v0.2 bundle plus this template's initiative and risk rules.

Usage: uv run skills/okf/validate.py [bundle-dir]   (default: .okf)
Exit 0 when clean, 1 when any error is found.
"""
import re
import sys
from datetime import date, datetime, timezone
from pathlib import Path

import yaml

PHASES = {"frame", "scout", "design", "production", "done"}
GATED = {"production", "done"}
RISK_STATES = {"open", "settled", "accepted"}
DATE_HEADING = re.compile(r"^## \d{4}-\d{2}-\d{2}\s*$")


def frontmatter(text):
    """Return (has_block, data, error)."""
    if not text.startswith("---\n"):
        return False, None, None
    end = text.find("\n---", 3)
    if end == -1:
        return True, None, "frontmatter block is not closed"
    try:
        data = yaml.safe_load(text[4:end]) or {}
    except yaml.YAMLError as e:
        return True, None, f"frontmatter is not valid YAML: {e}"
    if not isinstance(data, dict):
        return True, None, "frontmatter is not a mapping"
    return True, data, None


def moment(value):
    """Parse an OKF timestamp (YAML datetime, date, or ISO string) to aware UTC, else None."""
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return None
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    if isinstance(value, date):
        return datetime(value.year, value.month, value.day, tzinfo=timezone.utc)
    return None


def latest_human_signoff(data):
    """Latest `at` among human: verified entries; datetime.min if one lacks a time; None if none."""
    v = data.get("verified")
    entries = [v] if isinstance(v, dict) else v if isinstance(v, list) else []
    times = [
        moment(e.get("at")) or datetime.min.replace(tzinfo=timezone.utc)
        for e in entries
        if isinstance(e, dict) and str(e.get("by", "")).startswith("human:")
    ]
    return max(times) if times else None


def check(root):
    errors, concepts = [], {}
    for path in sorted(root.rglob("*.md")):
        rel = path.relative_to(root)
        text = path.read_text(encoding="utf-8")
        has, data, err = frontmatter(text)
        if path.name == "index.md":
            if has and (path.parent != root or err or set(data) - {"okf_version"}):
                errors.append((rel, "index.md carries frontmatter (only the bundle-root index may, with okf_version alone)"))
        elif path.name == "log.md":
            if has:
                errors.append((rel, "log.md carries frontmatter"))
            bad = [l for l in text.splitlines() if l.startswith("## ") and not DATE_HEADING.match(l)]
            if bad:
                errors.append((rel, f"log date heading is not YYYY-MM-DD: {bad[0]!r}"))
        elif not has:
            errors.append((rel, "missing YAML frontmatter"))
        elif err:
            errors.append((rel, err))
        elif not str(data.get("type") or "").strip():
            errors.append((rel, "frontmatter has no non-empty `type`"))
        else:
            concepts[path] = data

    for path, data in concepts.items():
        if data["type"] == "Risk" and data.get("state") not in RISK_STATES:
            errors.append((path.relative_to(root), f"Risk state {data.get('state')!r} is not one of {sorted(RISK_STATES)}"))
        if data["type"] != "Initiative":
            continue
        rel, phase = path.relative_to(root), data.get("phase")
        if phase not in PHASES:
            errors.append((rel, f"Initiative phase {phase!r} is not one of {sorted(PHASES)}"))
            continue
        if phase not in GATED:
            continue
        signoff = latest_human_signoff(data)
        if signoff is None:
            errors.append((rel, f"Initiative is in {phase} without a `verified` entry by a human: actor (run the gate)"))
        for other, d in concepts.items():
            if other.parent != path.parent or d["type"] != "Design":
                continue
            orel = other.relative_to(root)
            if d.get("status") == "draft":
                errors.append((orel, f"Design is still draft while its initiative is in {phase} (reopen the gate)"))
            changed = moment((d.get("generated") or {}).get("at")) if isinstance(d.get("generated"), dict) else None
            if signoff is not None and changed is not None and changed > signoff:
                errors.append((rel, f"latest human sign-off predates the last change to {orel} (run the gate again)"))
    return errors


def main():
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".okf")
    if not root.is_dir():
        print(f"ERROR {root}: not a directory")
        return 1
    errors = check(root)
    for rel, msg in errors:
        print(f"ERROR {rel}: {msg}")
    print(f"{'FAIL' if errors else 'OK'}: {root} ({len(errors)} error{'s' * (len(errors) != 1)})")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())

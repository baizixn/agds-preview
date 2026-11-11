#!/usr/bin/env python3
"""Dependency-free structural check for this Candidate Skill.

This is a local fallback when the bundled quick_validate.py cannot import
PyYAML. It does not replace the official validator or behavioral review.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


NAME_RE = re.compile(r"^[a-z0-9-]{1,63}$")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("skill_root", type=Path)
    parser.add_argument("--json-output", type=Path)
    args = parser.parse_args()
    root = args.skill_root.resolve()
    skill = root / "SKILL.md"
    errors = []
    if not skill.is_file():
        errors.append("SKILL.md missing")
        text = ""
    else:
        text = skill.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        errors.append("frontmatter opening delimiter missing")
    parts = text.split("---", 2)
    frontmatter = parts[1] if len(parts) == 3 else ""
    name_match = re.search(r"(?m)^name:\s*([^\n]+)$", frontmatter)
    description_match = re.search(r"(?m)^description:\s*(.+)$", frontmatter)
    name = name_match.group(1).strip() if name_match else ""
    description = description_match.group(1).strip() if description_match else ""
    if not NAME_RE.fullmatch(name):
        errors.append("frontmatter name is missing or invalid")
    if name and root.name != name:
        errors.append("folder name does not match frontmatter name")
    if not description:
        errors.append("frontmatter description missing")
    if "TODO" in text or "[TODO" in text:
        errors.append("unfinished scaffold marker found")
    required = [
        root / "references" / "vfx-authoring.md",
        root / "references" / "lighting-authoring.md",
        root / "references" / "evidence-and-handoff.md",
        root / "scripts" / "validate_realtime_art.py",
        root / "scripts" / "run_fixture_matrix.py",
        root / "scripts" / "build_hash_manifest.py",
    ]
    for path in required:
        if not path.is_file():
            errors.append(f"required resource missing: {path.relative_to(root).as_posix()}")
    result = {
        "validator": "candidate-dependency-free-structure-v1",
        "official_quick_validate_replacement": False,
        "skill_root": str(root),
        "valid": not errors,
        "errors": errors,
    }
    output = json.dumps(result, ensure_ascii=False, indent=2)
    print(output)
    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(output + "\n", encoding="utf-8")
    return 0 if not errors else 2


if __name__ == "__main__":
    raise SystemExit(main())

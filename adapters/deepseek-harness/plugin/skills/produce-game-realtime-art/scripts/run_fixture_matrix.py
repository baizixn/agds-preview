#!/usr/bin/env python3
"""Run a finite expected-valid/expected-invalid N4 static fixture matrix."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--matrix", type=Path, required=True)
    parser.add_argument("--validator", type=Path, required=True)
    parser.add_argument("--json-output", type=Path, required=True)
    args = parser.parse_args()
    matrix = json.loads(args.matrix.read_text(encoding="utf-8"))
    base = args.matrix.parent
    results = []
    all_pass = True
    for case in matrix["cases"]:
        definition = (base / case["definition"]).resolve()
        source = (base / case["source"]).resolve()
        manifest = (base / case["manifest"]).resolve()
        proc = subprocess.run(
            [
                sys.executable,
                str(args.validator.resolve()),
                "--kind",
                case["kind"],
                "--definition",
                str(definition),
                "--source",
                str(source),
                "--manifest",
                str(manifest),
            ] + (["--binding", str((base / case["binding"]).resolve())] if case.get("binding") else []),
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )
        try:
            validation = json.loads(proc.stdout)
        except json.JSONDecodeError:
            validation = {"valid": False, "errors": ["validator output was not JSON"], "raw": proc.stdout}
        actual_valid = bool(validation.get("valid"))
        case_pass = actual_valid is bool(case["expected_valid"])
        all_pass = all_pass and case_pass
        results.append(
            {
                "id": case["id"],
                "failure_class": case["failure_class"],
                "expected_valid": case["expected_valid"],
                "actual_valid": actual_valid,
                "matrix_result": "Pass" if case_pass else "Fail",
                "validator_exit_code": proc.returncode,
                "validator_errors": validation.get("errors", []),
                "evidence_tier": "static_source",
            }
        )
    report = {
        "matrix_id": matrix["matrix_id"],
        "case_count": len(results),
        "result": "Pass" if all_pass else "Fail",
        "runtime_claims": "Not Run",
        "cases": results,
    }
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if all_pass else 3


if __name__ == "__main__":
    sys.exit(main())

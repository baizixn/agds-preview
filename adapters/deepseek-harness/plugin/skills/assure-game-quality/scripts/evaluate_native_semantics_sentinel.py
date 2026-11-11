from __future__ import annotations

import argparse
import json
from pathlib import Path


TOP_FIELDS = {"schema_version", "claim_type", "route_identity", "required_semantics", "observations", "dependent_assertions", "qa_owned_cleanup_targets"}
ROUTE_FIELDS = {"browser", "runtime", "profile", "driver", "fixture", "event_contract", "persistence_path"}
OBSERVATION_FIELDS = {"semantic", "expected", "actual", "status"}
ASSERTION_FIELDS = {"id", "current_result"}
CLEANUP_FIELDS = {"id", "owner"}
RESULTS = {"Pass", "Fail", "Inconclusive", "Not Run"}
CLAIM_TYPES = {"read_only", "browser_semantics"}


def nonempty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def evaluate(payload: dict) -> tuple[int, dict]:
    diagnostics: list[str] = []
    if not isinstance(payload, dict):
        payload = {}
        diagnostics.append("input must be an object")
    extra = sorted(set(payload) - TOP_FIELDS)
    if extra:
        diagnostics.append("unknown top-level fields: " + ", ".join(extra))
    if type(payload.get("schema_version")) is not int or payload.get("schema_version") != 1:
        diagnostics.append("schema_version must equal 1")
    if payload.get("claim_type") not in CLAIM_TYPES:
        diagnostics.append("claim_type must be read_only or browser_semantics")
    required = payload.get("required_semantics")
    observations = payload.get("observations")
    assertions = payload.get("dependent_assertions")
    cleanup = payload.get("qa_owned_cleanup_targets")
    if not isinstance(required, list) or not all(nonempty_string(item) for item in required) or len(required) != len(set(required)):
        diagnostics.append("required_semantics must be a duplicate-free string list")
        required = []
    if not isinstance(observations, list):
        diagnostics.append("observations must be a list")
        observations = []
    if not isinstance(assertions, list):
        diagnostics.append("dependent_assertions must be a list")
        assertions = []
    if not isinstance(cleanup, list):
        diagnostics.append("qa_owned_cleanup_targets must be a list")
        cleanup = []

    route = payload.get("route_identity")
    if not isinstance(route, dict):
        diagnostics.append("route_identity must be an object")
        route = {}
    route_extra = sorted(set(route) - ROUTE_FIELDS)
    if route_extra:
        diagnostics.append("unknown route_identity fields: " + ", ".join(route_extra))

    if payload.get("claim_type") == "read_only":
        if required or observations or assertions or cleanup:
            diagnostics.append("read_only route must not contain semantic observations, dependent assertions, or cleanup targets")
        if route:
            diagnostics.append("read_only route_identity must be empty")
        output = {
            "sentinel": "not_required" if not diagnostics else "Inconclusive",
            "evidence_eligible": not diagnostics,
            "dependent_results": [], "limitation_class": None if not diagnostics else "test_or_infrastructure",
            "product_revision_allowed": False, "cleanup_targets": [], "diagnostics": diagnostics,
        }
        return (0 if not diagnostics else 1), output

    route_missing = sorted(field for field in ROUTE_FIELDS if not nonempty_string(route.get(field)))
    if route_missing:
        diagnostics.append("missing route_identity fields: " + ", ".join(route_missing))
    if not required:
        diagnostics.append("browser_semantics requires at least one required semantic")
    statuses: dict[str, str] = {}
    for index, item in enumerate(observations):
        label = f"observations[{index}]"
        if not isinstance(item, dict):
            diagnostics.append(f"{label} must be an object")
            continue
        item_extra = sorted(set(item) - OBSERVATION_FIELDS)
        missing = sorted(OBSERVATION_FIELDS - set(item))
        if item_extra:
            diagnostics.append(f"{label} unknown fields: {', '.join(item_extra)}")
        if missing:
            diagnostics.append(f"{label} missing fields: {', '.join(missing)}")
        for field in ("semantic", "expected", "actual"):
            if field in item and not nonempty_string(item[field]):
                diagnostics.append(f"{label} {field} must be a non-empty string")
        if item.get("status") not in {"Pass", "Fail", "Inconclusive"}:
            diagnostics.append(f"{label} invalid status")
        semantic = item.get("semantic")
        if semantic not in required:
            diagnostics.append(f"{label} semantic is not required")
        elif semantic in statuses:
            diagnostics.append(f"{label} duplicate semantic")
        else:
            statuses[semantic] = item.get("status")

    clean_ids: list[str] = []
    seen_cleanup: set[str] = set()
    for index, item in enumerate(cleanup):
        label = f"qa_owned_cleanup_targets[{index}]"
        if not isinstance(item, dict) or set(item) != CLEANUP_FIELDS:
            diagnostics.append(f"{label} must contain exactly id and owner")
            continue
        if not nonempty_string(item.get("id")) or item.get("owner") != "qa":
            diagnostics.append(f"{label} ownership not proven")
            continue
        if item["id"] in seen_cleanup:
            diagnostics.append(f"{label} duplicate id")
            continue
        seen_cleanup.add(item["id"])
        clean_ids.append(item["id"])

    dependent_results: list[dict[str, str]] = []
    seen_assertions: set[str] = set()
    for index, item in enumerate(assertions):
        label = f"dependent_assertions[{index}]"
        if not isinstance(item, dict) or set(item) != ASSERTION_FIELDS:
            diagnostics.append(f"{label} must contain exactly id and current_result")
            continue
        if not nonempty_string(item.get("id")):
            diagnostics.append(f"{label} id must be a non-empty string")
            continue
        if item["id"] in seen_assertions:
            diagnostics.append(f"{label} duplicate id")
            continue
        seen_assertions.add(item["id"])
        current = item.get("current_result")
        if current not in RESULTS:
            diagnostics.append(f"{label} current_result must be Pass, Fail, Inconclusive, or Not Run")
            continue
        dependent_results.append({"id": item["id"], "result": current})

    if diagnostics:
        sentinel = "Inconclusive"
    elif any(statuses.get(item) == "Fail" for item in required):
        sentinel = "Fail"
    elif all(statuses.get(item) == "Pass" for item in required):
        sentinel = "Pass"
    else:
        sentinel = "Inconclusive"
    eligible = sentinel == "Pass" and not diagnostics
    if not eligible:
        dependent_results = [
            {"id": item["id"], "result": "Not Run" if item["result"] == "Not Run" else "Inconclusive"}
            for item in dependent_results
        ]
    output = {
        "sentinel": sentinel,
        "evidence_eligible": eligible,
        "dependent_results": sorted(dependent_results, key=lambda value: value["id"]),
        "limitation_class": None if eligible else "test_or_infrastructure",
        "product_revision_allowed": False,
        "cleanup_targets": sorted(clean_ids) if not diagnostics else [],
        "diagnostics": diagnostics,
    }
    return (0 if sentinel == "Pass" and not diagnostics else 1), output


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    args = parser.parse_args()
    code, output = evaluate(json.loads(args.input.read_text(encoding="utf-8")))
    print(json.dumps(output, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
    return code


if __name__ == "__main__":
    raise SystemExit(main())

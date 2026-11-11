from __future__ import annotations

import argparse
import json
from pathlib import Path


TOP_FIELDS = {"schema_version", "mode", "owner_authorization_ref", "contract", "research"}
CONTRACT_FIELDS = {
    "id", "revision", "state", "target_player", "use_context", "stage",
    "decision_question", "player_promise", "quality_floor", "falsifiers",
    "evidence_cutoff", "approved_contract_ref", "changed_dimensions",
}
RESEARCH_FIELDS = {
    "constraints", "validation_authority", "hypothesis", "downstream_decision",
    "downstream_recipient", "in_scope_dimensions", "excluded_dimensions",
    "evidence_cutoff",
}
RESEARCH_LIST_FIELDS = {"constraints", "in_scope_dimensions", "excluded_dimensions"}


def nonempty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def string_list(value: object, *, nonempty: bool) -> bool:
    return (
        isinstance(value, list)
        and (bool(value) or not nonempty)
        and all(nonempty_string(item) for item in value)
        and len(value) == len(set(value))
    )


def evaluate(payload: dict) -> tuple[int, dict]:
    diagnostics: list[str] = []
    if not isinstance(payload, dict):
        payload = {}
        diagnostics.append("input must be an object")
    unknown = sorted(set(payload) - TOP_FIELDS)
    if unknown:
        diagnostics.append("unknown top-level fields: " + ", ".join(unknown))
    if type(payload.get("schema_version")) is not int or payload.get("schema_version") != 1:
        diagnostics.append("schema_version must equal 1")
    contract = payload.get("contract")
    if not isinstance(contract, dict):
        diagnostics.append("contract must be an object")
        contract = {}
    contract_unknown = sorted(set(contract) - CONTRACT_FIELDS)
    if contract_unknown:
        diagnostics.append("unknown contract fields: " + ", ".join(contract_unknown))
    mode = payload.get("mode")
    if not nonempty_string(mode) or mode not in {"formation", "delivery"}:
        diagnostics.append("mode must be formation or delivery")

    missing: list[str] = []
    for field in ("id", "state", "target_player", "use_context", "stage"):
        if not nonempty_string(contract.get(field)):
            missing.append(field)
    if type(contract.get("revision")) is not int or contract.get("revision", 0) < 1:
        missing.append("revision")

    result = "invalid"
    if mode == "formation":
        if not nonempty_string(payload.get("owner_authorization_ref")):
            missing.append("owner_authorization_ref")
        for field in ("decision_question", "player_promise", "quality_floor", "evidence_cutoff"):
            if not nonempty_string(contract.get(field)):
                missing.append(field)
        if not string_list(contract.get("falsifiers"), nonempty=True):
            missing.append("falsifiers")
        if contract.get("state") != "candidate":
            diagnostics.append("formation contract state must be candidate")
        for incompatible in ("approved_contract_ref", "changed_dimensions"):
            if incompatible in contract:
                diagnostics.append(f"formation contract must not contain {incompatible}")
        result = "valid_candidate"
    elif mode == "delivery":
        if "owner_authorization_ref" in payload:
            diagnostics.append("delivery packet must not contain owner_authorization_ref")
        if not nonempty_string(contract.get("approved_contract_ref")):
            missing.append("approved_contract_ref")
        if contract.get("state") != "approved":
            diagnostics.append("delivery contract state must be approved")
        if "changed_dimensions" in contract and not string_list(contract.get("changed_dimensions"), nonempty=False):
            diagnostics.append("changed_dimensions must be a duplicate-free string list")
        for incompatible in ("decision_question", "player_promise", "quality_floor", "falsifiers", "evidence_cutoff"):
            if incompatible in contract:
                diagnostics.append(f"delivery contract must not contain {incompatible}")
        result = "reuse_approved"

    research_requested = "research" in payload
    if research_requested:
        research = payload.get("research")
        if not isinstance(research, dict):
            diagnostics.append("research must be an object")
        else:
            research_unknown = sorted(set(research) - RESEARCH_FIELDS)
            if research_unknown:
                diagnostics.append("unknown research fields: " + ", ".join(research_unknown))
            for field in sorted(RESEARCH_FIELDS):
                if field not in research:
                    missing.append(f"research.{field}")
                elif field in RESEARCH_LIST_FIELDS:
                    if not string_list(research.get(field), nonempty=True):
                        diagnostics.append(
                            f"research.{field} must be a non-empty duplicate-free string list"
                        )
                elif not nonempty_string(research.get(field)):
                    diagnostics.append(f"research.{field} must be a non-empty string")

    if missing:
        diagnostics.append("missing required fields: " + ", ".join(sorted(set(missing))))
    if diagnostics:
        structural_only = all(message.startswith("missing required fields:") for message in diagnostics)
        result = "missing_input" if missing and structural_only else "invalid"
    output = {
        "result": result,
        "contract_state": contract.get("state") if nonempty_string(contract.get("state")) else "unknown",
        "missing_fields": sorted(set(missing)),
        "reusable_contract_ref": contract.get("approved_contract_ref") if result == "reuse_approved" else None,
        "owner_decision": "not_decided",
        "diagnostics": diagnostics,
    }
    if research_requested:
        output["eligible_for_research"] = result in {"valid_candidate", "reuse_approved"}
    return (0 if result in {"valid_candidate", "reuse_approved"} else 1), output


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    args = parser.parse_args()
    payload = json.loads(args.input.read_text(encoding="utf-8"))
    code, output = evaluate(payload)
    print(json.dumps(output, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
    return code


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re


TOP_FIELDS = {"schema_version", "checkpoint_required", "qa_gap", "current_checkpoint", "event"}
GAP_FIELDS = {
    "request_id", "checkpoint_id", "claim_ref", "contract_ref", "target_ref",
    "environment_ref", "evidence_role", "qualification_authority_ref",
    "participant_binding_ref", "participation_state", "steps", "max_attempts",
    "exit_conditions", "evidence_requested", "prohibited_conclusions",
}
BINDING_FIELDS = {
    "claim_ref", "contract_ref", "target_ref", "environment_ref",
    "participant_binding_ref",
}
CURRENT_FIELDS = {
    "checkpoint_id", "state", "request_count", "closure_reason",
    "observation_ref",
} | BINDING_FIELDS
EVENT_FIELDS = {"type", "observation_ref"}
EVENTS = {"observation", "refusal", "unavailable", "exit_condition"}
CLOSURE_REASONS = EVENTS - {"observation"}
STATES = {"open", "completed_pending_qa", "closed_unresolved"}
PARTICIPATION_STATES = {"requested", "available", "unavailable", "refused"}
PARTICIPANT_BINDING_PATTERN = re.compile(r"participant-[0-9a-f]{32}\Z")


def nonempty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def nonempty_string_list(value: object) -> bool:
    return isinstance(value, list) and bool(value) and all(nonempty_string(item) for item in value) and len(value) == len(set(value))


def invalid_output(diagnostics: list[str]) -> tuple[int, dict]:
    return 1, {
        "checkpoint_state": "invalid", "request_count": 0,
        "visibility_contract": "invalid", "closure_reason": None,
        "observation_ref": None, "qa_evidence_update_required": False,
        "reviewer_entry": "blocked_invalid_checkpoint", "owner_decision": "not_decided",
        "next_request": None, "diagnostics": diagnostics,
        **{field: None for field in BINDING_FIELDS},
    }


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
    if type(payload.get("checkpoint_required")) is not bool:
        diagnostics.append("checkpoint_required must be boolean")
    if payload.get("checkpoint_required") is False:
        if payload.get("qa_gap") is not None or payload.get("current_checkpoint") is not None or payload.get("event") is not None:
            diagnostics.append("not-required checkpoint must not contain qa_gap, current_checkpoint, or event")
        if diagnostics:
            return invalid_output(diagnostics)
        return 0, {
            "checkpoint_state": "not_required", "request_count": 0,
            "visibility_contract": "unchanged", "closure_reason": None,
            "observation_ref": None, "qa_evidence_update_required": False,
            "reviewer_entry": "allowed", "owner_decision": "not_decided",
            "next_request": None, "diagnostics": [],
            **{field: None for field in BINDING_FIELDS},
        }

    gap = payload.get("qa_gap")
    if not isinstance(gap, dict):
        diagnostics.append("qa_gap must be an object")
        gap = {}
    gap_extra = sorted(set(gap) - GAP_FIELDS)
    missing = sorted(GAP_FIELDS - set(gap))
    if gap_extra:
        diagnostics.append("unknown qa_gap fields: " + ", ".join(gap_extra))
    if missing:
        diagnostics.append("missing qa_gap fields: " + ", ".join(missing))
    for field in GAP_FIELDS - {"steps", "exit_conditions", "evidence_requested", "prohibited_conclusions", "max_attempts"}:
        if field in gap and not nonempty_string(gap[field]):
            diagnostics.append(f"qa_gap {field} must be a non-empty string")
    for field in ("steps", "exit_conditions", "evidence_requested", "prohibited_conclusions"):
        if field in gap and not nonempty_string_list(gap[field]):
            diagnostics.append(f"qa_gap {field} must be a non-empty duplicate-free string list")
    if type(gap.get("max_attempts")) is not int or gap.get("max_attempts") != 1:
        diagnostics.append("max_attempts must equal 1")
    participation_state = gap.get("participation_state")
    if not nonempty_string(participation_state) or participation_state not in PARTICIPATION_STATES:
        diagnostics.append("participation_state is invalid")
    participant = gap.get("participant_binding_ref")
    if not nonempty_string(participant) or PARTICIPANT_BINDING_PATTERN.fullmatch(participant) is None:
        diagnostics.append("participant_binding_ref must be an opaque participant token")

    current = payload.get("current_checkpoint")
    if current is not None:
        if not isinstance(current, dict):
            diagnostics.append("current_checkpoint must be an object")
            current = None
        else:
            current_extra = sorted(set(current) - CURRENT_FIELDS)
            current_missing = sorted(CURRENT_FIELDS - set(current))
            if current_extra:
                diagnostics.append("unknown current_checkpoint fields: " + ", ".join(current_extra))
            if current_missing:
                diagnostics.append("missing current_checkpoint fields: " + ", ".join(current_missing))
            if current.get("checkpoint_id") != gap.get("checkpoint_id"):
                diagnostics.append("checkpoint identity mismatch")
            for field in sorted(BINDING_FIELDS):
                if not nonempty_string(current.get(field)):
                    diagnostics.append(f"current checkpoint {field} must be a non-empty string")
                elif current.get(field) != gap.get(field):
                    diagnostics.append(f"current checkpoint {field} binding mismatch")
            if not nonempty_string(current.get("state")) or current.get("state") not in STATES:
                diagnostics.append("current checkpoint state is invalid")
            if type(current.get("request_count")) is not int or current.get("request_count") != 1:
                diagnostics.append("current request_count must equal 1")
            state = current.get("state")
            if state == "open" and (current.get("closure_reason") is not None or current.get("observation_ref") is not None):
                diagnostics.append("open checkpoint cannot contain closure_reason or observation_ref")
            if state == "completed_pending_qa" and not nonempty_string(current.get("observation_ref")):
                diagnostics.append("completed_pending_qa requires observation_ref")
            if state == "completed_pending_qa" and current.get("closure_reason") is not None:
                diagnostics.append("completed_pending_qa cannot contain closure_reason")
            closure_reason = current.get("closure_reason")
            if state == "closed_unresolved" and (
                not nonempty_string(closure_reason) or closure_reason not in CLOSURE_REASONS
            ):
                diagnostics.append("closed_unresolved closure_reason is invalid")
            if state == "closed_unresolved" and current.get("observation_ref") is not None:
                diagnostics.append("closed_unresolved cannot contain observation_ref")

    event = payload.get("event")
    if event is not None:
        if not isinstance(event, dict):
            diagnostics.append("event must be an object")
            event = None
        else:
            event_extra = sorted(set(event) - EVENT_FIELDS)
            if event_extra:
                diagnostics.append("unknown event fields: " + ", ".join(event_extra))
            event_type = event.get("type")
            if not nonempty_string(event_type) or event_type not in EVENTS:
                diagnostics.append("invalid event type")
            if event.get("type") == "observation":
                if not nonempty_string(event.get("observation_ref")):
                    diagnostics.append("observation event requires observation_ref")
            elif "observation_ref" in event and event.get("observation_ref") is not None:
                diagnostics.append("non-observation event must not contain observation_ref")
    if current is None and event is not None:
        diagnostics.append("event requires an existing open checkpoint")
    terminal_replay = False
    if current is not None and current.get("state") != "open" and event is not None:
        terminal_replay = (
            current.get("state") == "closed_unresolved"
            and event.get("type") == current.get("closure_reason")
            and event.get("observation_ref") is None
        ) or (
            current.get("state") == "completed_pending_qa"
            and event.get("type") == "observation"
            and event.get("observation_ref") == current.get("observation_ref")
        )
        if not terminal_replay:
            diagnostics.append("closed checkpoint accepts only an identical terminal-event replay")
    if diagnostics:
        return invalid_output(diagnostics)

    if current is None:
        state, closure, observation = "open", None, None
    elif event is None or terminal_replay:
        state, closure, observation = current["state"], current["closure_reason"], current["observation_ref"]
    elif event["type"] == "observation":
        state, closure, observation = "completed_pending_qa", None, event["observation_ref"]
    else:
        state, closure, observation = "closed_unresolved", event["type"], None
    output = {
        "checkpoint_state": state,
        "request_count": 1,
        "visibility_contract": "checkpoint_required" if state == "open" else "bounded_checkpoint_closed",
        "closure_reason": closure,
        "observation_ref": observation,
        "qa_evidence_update_required": state == "completed_pending_qa",
        "reviewer_entry": "blocked_pending_checkpoint" if state == "open" else ("pending_qa" if state == "completed_pending_qa" else "allowed_with_unresolved_risk"),
        "owner_decision": "not_decided",
        "next_request": None,
        "diagnostics": [],
        **{field: gap[field] for field in BINDING_FIELDS},
    }
    return 0, output


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    args = parser.parse_args()
    code, output = evaluate(json.loads(args.input.read_text(encoding="utf-8")))
    print(json.dumps(output, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
    return code


if __name__ == "__main__":
    raise SystemExit(main())

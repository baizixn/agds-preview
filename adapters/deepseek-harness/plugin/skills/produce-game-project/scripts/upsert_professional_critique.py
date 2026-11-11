from __future__ import annotations

import argparse
import json
from pathlib import Path


TOP_FIELDS = {"schema_version", "contract_ref", "checkpoint", "obligations", "existing_records", "updates"}
CHECKPOINT_FIELDS = {"id", "trace_row_id", "snapshot"}
OBLIGATION_FIELDS = {"slot", "responsible_owner"}
UPDATE_FIELDS = {"critique_id", "slot", "source_owner", "source_update_id", "record_revision", "relation", "evidence_ref", "freshness"}
RELATIONS = {"Supports", "Falsifies", "Inconclusive", "Not Run"}
FRESHNESS = {"current", "stale", "unknown"}


def nonempty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def canonical_update(item: dict) -> dict:
    return {key: item[key] for key in sorted(UPDATE_FIELDS)}


def validate_record(item: object, label: str, owners: dict[str, str], diagnostics: list[str]) -> dict | None:
    if not isinstance(item, dict):
        diagnostics.append(f"{label} must be an object")
        return None
    extra = sorted(set(item) - UPDATE_FIELDS)
    missing = sorted(UPDATE_FIELDS - set(item))
    if extra:
        diagnostics.append(f"{label} unknown fields: {', '.join(extra)}")
    if missing:
        diagnostics.append(f"{label} missing fields: {', '.join(missing)}")
    for field in ("critique_id", "slot", "source_owner", "source_update_id", "evidence_ref"):
        if field in item and not nonempty_string(item[field]):
            diagnostics.append(f"{label} {field} must be a non-empty string")
    if type(item.get("record_revision")) is not int or item.get("record_revision", 0) < 1:
        diagnostics.append(f"{label} record_revision must be a positive integer")
    if item.get("relation") not in RELATIONS:
        diagnostics.append(f"{label} invalid relation")
    if item.get("freshness") not in FRESHNESS:
        diagnostics.append(f"{label} invalid freshness")
    if item.get("slot") not in owners:
        diagnostics.append(f"{label} slot has no obligation")
    elif owners[item["slot"]] != item.get("source_owner"):
        diagnostics.append(f"{label} source_owner does not own slot")
    if extra or missing or any(message.startswith(label) for message in diagnostics):
        return None
    return canonical_update(item)


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
    if not nonempty_string(payload.get("contract_ref")):
        diagnostics.append("contract_ref must be a non-empty string")
    checkpoint = payload.get("checkpoint")
    if not isinstance(checkpoint, dict):
        diagnostics.append("checkpoint must be an object")
        checkpoint = {}
    checkpoint_unknown = sorted(set(checkpoint) - CHECKPOINT_FIELDS)
    checkpoint_missing = sorted(CHECKPOINT_FIELDS - set(checkpoint))
    if checkpoint_unknown:
        diagnostics.append("unknown checkpoint fields: " + ", ".join(checkpoint_unknown))
    if checkpoint_missing:
        diagnostics.append("missing checkpoint fields: " + ", ".join(checkpoint_missing))
    for field in CHECKPOINT_FIELDS:
        if field in checkpoint and not nonempty_string(checkpoint[field]):
            diagnostics.append(f"checkpoint {field} must be a non-empty string")

    obligations = payload.get("obligations")
    updates = payload.get("updates")
    existing = payload.get("existing_records")
    for name, items in (("obligations", obligations), ("existing_records", existing), ("updates", updates)):
        if not isinstance(items, list):
            diagnostics.append(f"{name} must be a list")
    obligations = obligations if isinstance(obligations, list) else []
    existing = existing if isinstance(existing, list) else []
    updates = updates if isinstance(updates, list) else []
    if not obligations:
        diagnostics.append("obligations must contain at least one responsibility slot")

    owners: dict[str, str] = {}
    for index, item in enumerate(obligations):
        label = f"obligations[{index}]"
        if not isinstance(item, dict):
            diagnostics.append(f"{label} must be an object")
            continue
        extra = sorted(set(item) - OBLIGATION_FIELDS)
        missing = sorted(OBLIGATION_FIELDS - set(item))
        if extra:
            diagnostics.append(f"{label} unknown fields: {', '.join(extra)}")
        if missing:
            diagnostics.append(f"{label} missing fields: {', '.join(missing)}")
        slot, owner = item.get("slot"), item.get("responsible_owner")
        if not nonempty_string(slot) or not nonempty_string(owner):
            diagnostics.append(f"{label} slot and responsible_owner must be non-empty strings")
            continue
        if slot in owners:
            diagnostics.append(f"{label} duplicate slot")
            continue
        owners[slot] = owner

    records: dict[str, dict] = {}
    critique_ids: dict[str, str] = {}
    for index, item in enumerate(existing):
        canonical = validate_record(item, f"existing_records[{index}]", owners, diagnostics)
        if canonical is None:
            continue
        update_id = canonical["source_update_id"]
        critique_id = canonical["critique_id"]
        if update_id in records:
            diagnostics.append(f"existing_records[{index}] duplicate source_update_id")
            continue
        if critique_id in critique_ids and critique_ids[critique_id] != update_id:
            diagnostics.append(f"existing_records[{index}] critique_id maps to multiple source updates")
            continue
        records[update_id] = canonical
        critique_ids[critique_id] = update_id

    grouped_updates: dict[str, list[dict]] = {}
    for index, item in enumerate(updates):
        canonical = validate_record(item, f"updates[{index}]", owners, diagnostics)
        if canonical is not None:
            grouped_updates.setdefault(canonical["source_update_id"], []).append(canonical)

    accepted: list[dict] = []
    noops: list[str] = []
    conflicts: list[str] = []
    if not diagnostics:
        for update_id in sorted(grouped_updates):
            variants = {json.dumps(item, ensure_ascii=False, sort_keys=True, separators=(",", ":")): item for item in grouped_updates[update_id]}
            if len(variants) > 1:
                conflicts.append(update_id)
                continue
            canonical = next(iter(variants.values()))
            duplicate_count = len(grouped_updates[update_id]) - 1
            if update_id in records:
                if records[update_id] == canonical:
                    noops.append(update_id)
                else:
                    conflicts.append(update_id)
                continue
            prior_update = critique_ids.get(canonical["critique_id"])
            if prior_update is not None and prior_update != update_id:
                conflicts.append(update_id)
                continue
            records[update_id] = canonical
            critique_ids[canonical["critique_id"]] = update_id
            accepted.append(canonical)
            noops.extend([update_id] * duplicate_count)

    updated_slots = {item["slot"] for item in records.values()} if not diagnostics else set()
    missing_obligations = sorted(slot for slot in owners if slot not in updated_slots)
    integration = [] if diagnostics or conflicts else [
        {"slot": item["slot"], "relation": item["relation"], "evidence_ref": item["evidence_ref"], "freshness": item["freshness"]}
        for item in sorted(records.values(), key=lambda value: (value["slot"], value["source_update_id"]))
    ]
    result = "invalid" if diagnostics else ("conflict" if conflicts else "updated")
    output = {
        "result": result,
        "accepted_updates": sorted(accepted, key=lambda value: value["source_update_id"]) if result == "updated" else [],
        "noops": sorted(noops) if result == "updated" else [],
        "conflicts": sorted(conflicts),
        "missing_obligations": missing_obligations,
        "pending_orchestrator_routes": [] if result != "updated" else [{"slot": slot, "responsible_owner": owners[slot]} for slot in missing_obligations],
        "game_design_integration_inputs": integration,
        "owner_decision": "not_decided",
        "diagnostics": diagnostics,
    }
    return (0 if result == "updated" else 1), output


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    args = parser.parse_args()
    code, output = evaluate(json.loads(args.input.read_text(encoding="utf-8")))
    print(json.dumps(output, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
    return code


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import argparse
import hashlib
import json
import unicodedata
from pathlib import Path
import re


def normalize_signal_text(value: str | None) -> str:
    normalized = unicodedata.normalize("NFKC", value or "").strip().lower()
    return " ".join(normalized.split())


def build_signal_group_id(
    *,
    responsible_agent: str,
    responsible_owned_skill: str | None,
    category: str,
    observed_behavior: str,
    expected_behavior: str,
) -> str:
    # Category is recorded for analysis but excluded from identity so a later
    # classification refinement cannot split one underlying signal into two.
    fields = (
        responsible_agent,
        responsible_owned_skill or "",
        observed_behavior,
        expected_behavior,
    )
    payload = "|".join(normalize_signal_text(field) for field in fields)
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:12]
    return f"cap-{digest}"


PROPOSAL_DECISIONS = {
    "minimal_single_component_candidate",
    "update_existing_group_only",
    "scope_expansion_approval_required",
}
NO_PROPOSAL_DECISIONS = {
    "no_shared_proposal",
    "ownership_or_scope_question",
}
ALL_PROPOSAL_DECISIONS = PROPOSAL_DECISIONS | NO_PROPOSAL_DECISIONS
CANONICAL_FACT_PATTERNS = (
    ("project", r"\bproject\b"),
    ("engine", r"\bengine\b"),
    ("platform", r"\b(?:platform|headset)\b"),
    ("gameplay", r"\bgameplay\b"),
    ("code", r"\b(?:code|implementation)\b"),
    ("status", r"\b(?:status|blocked)\b"),
    ("test", r"\b(?:test|regression)\b"),
)
REUSABLE_PROJECT_TERMS = (
    "bootstrap-game-project",
    "project-bootstrap",
    "project-memory",
    "project owner",
)
DUPLICATE_STABLE_FIELDS = (
    "reuse_scope",
    "responsible_agent",
    "responsible_owned_skill",
    "affected_component",
    "affected_components",
    "scope_expansion_required",
    "excluded_fact_types",
    "regression_evaluations",
)


def detect_project_fact_types(source: dict) -> list[str]:
    source_text = f"{source['observed_behavior']} {source['expected_behavior']}".lower()
    for reusable_term in REUSABLE_PROJECT_TERMS:
        source_text = source_text.replace(reusable_term, "")
    return [
        fact_type
        for fact_type, pattern in CANONICAL_FACT_PATTERNS
        if re.search(pattern, source_text)
    ]


def finalize_capability_payload(raw_signals: dict, agent_output: dict) -> dict:
    source_by_id = {item["id"]: item for item in raw_signals["signals"]}
    finalized_by_id: dict[str, dict] = {}

    for item in agent_output["signals"]:
        signal_id = item["id"]
        if signal_id not in source_by_id:
            raise ValueError(f"unknown signal id: {signal_id}")
        source = source_by_id[signal_id]
        decision = item["proposal_decision"]

        if decision not in ALL_PROPOSAL_DECISIONS:
            raise ValueError(f"unknown proposal decision for {signal_id}: {decision}")

        supplied_fact_types = item.get("excluded_fact_types") or []
        canonical_fact_types = {fact_type for fact_type, _ in CANONICAL_FACT_PATTERNS}
        unknown_fact_types = set(supplied_fact_types) - canonical_fact_types
        if unknown_fact_types:
            raise ValueError(
                f"unknown excluded fact types for {signal_id}: {sorted(unknown_fact_types)}"
            )
        merged_fact_types = set(supplied_fact_types) | set(detect_project_fact_types(source))
        item["excluded_fact_types"] = [
            fact_type
            for fact_type, _ in CANONICAL_FACT_PATTERNS
            if fact_type in merged_fact_types
        ]

        if decision in NO_PROPOSAL_DECISIONS:
            if item.get("duplicate_of") is not None:
                raise ValueError(
                    f"no-proposal decision for {signal_id} cannot reference a duplicate"
                )
            item["signal_group_id"] = None
            item["proposal_id"] = None
            item["proposal_summary"] = None
            item["regression_evaluations"] = None
            item["affected_component"] = None
            item["affected_components"] = []
            item["scope_expansion_required"] = False
            finalized_by_id[signal_id] = item
            continue

        duplicate_of = item.get("duplicate_of")
        if decision == "update_existing_group_only":
            if not duplicate_of:
                raise ValueError(
                    f"update_existing_group_only for {signal_id} requires duplicate_of"
                )
            original = finalized_by_id.get(duplicate_of)
            if original is None:
                raise ValueError(f"duplicate {signal_id} references unavailable signal {duplicate_of}")
            if (
                original.get("proposal_decision") not in PROPOSAL_DECISIONS
                or not original.get("signal_group_id")
            ):
                raise ValueError(
                    f"duplicate {signal_id} references signal {duplicate_of} without a proposal"
                )
            original_source = source_by_id[duplicate_of]
            for field in ("observed_behavior", "expected_behavior"):
                if normalize_signal_text(source[field]) != normalize_signal_text(
                    original_source[field]
                ):
                    raise ValueError(
                        f"duplicate {signal_id} does not match {duplicate_of} on {field}"
                    )
            for field in DUPLICATE_STABLE_FIELDS:
                item[field] = original[field]
            item["signal_group_id"] = original["signal_group_id"]
            item["proposal_id"] = original["proposal_id"]
            item["proposal_summary"] = original["proposal_summary"]
            finalized_by_id[signal_id] = item
            continue

        if duplicate_of is not None:
            raise ValueError(
                f"{decision} for {signal_id} cannot reference duplicate_of"
            )

        if decision == "minimal_single_component_candidate":
            owned_skill = item.get("responsible_owned_skill")
            if (
                not item.get("responsible_agent")
                or not owned_skill
                or item.get("affected_component") != owned_skill
                or item.get("affected_components") != [owned_skill]
                or item.get("scope_expansion_required") is not False
            ):
                raise ValueError(
                    f"invalid single-component proposal shape for {signal_id}"
                )

        identity_agent = item.get("responsible_agent") or ""
        identity_skill = item.get("responsible_owned_skill")
        if decision == "scope_expansion_approval_required":
            components = sorted(set(item.get("affected_components") or []))
            if len(components) < 2:
                raise ValueError(
                    f"scope expansion for {signal_id} requires at least two components"
                )
            item["responsible_agent"] = None
            item["responsible_owned_skill"] = None
            item["affected_component"] = None
            item["affected_components"] = components
            item["scope_expansion_required"] = True
            identity_agent = "cross-cutting"
            identity_skill = ",".join(components)

        group_id = build_signal_group_id(
            responsible_agent=identity_agent,
            responsible_owned_skill=identity_skill,
            category=item["category"],
            observed_behavior=source["observed_behavior"],
            expected_behavior=source["expected_behavior"],
        )
        item["signal_group_id"] = group_id
        item["proposal_id"] = group_id.replace("cap-", "prop-", 1)
        item["proposal_summary"] = normalize_signal_text(source["expected_behavior"])
        finalized_by_id[signal_id] = item

    return agent_output


def main() -> None:
    parser = argparse.ArgumentParser(description="Build or finalize capability signal IDs.")
    parser.add_argument("--responsible-agent")
    parser.add_argument("--responsible-owned-skill", default="")
    parser.add_argument("--category")
    parser.add_argument("--observed-behavior")
    parser.add_argument("--expected-behavior")
    parser.add_argument("--signals-file", type=Path)
    parser.add_argument("--agent-output", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    if args.signals_file or args.agent_output or args.output:
        if not args.signals_file or not args.agent_output:
            parser.error("--signals-file and --agent-output are required for finalization")
        raw_signals = json.loads(args.signals_file.read_text(encoding="utf-8"))
        agent_output = json.loads(args.agent_output.read_text(encoding="utf-8"))
        finalized = finalize_capability_payload(raw_signals, agent_output)
        serialized = json.dumps(finalized, ensure_ascii=False, indent=2) + "\n"
        if args.output:
            args.output.write_text(serialized, encoding="utf-8")
        else:
            print(serialized, end="")
        return

    missing = [
        name
        for name, value in (
            ("--responsible-agent", args.responsible_agent),
            ("--category", args.category),
            ("--observed-behavior", args.observed_behavior),
            ("--expected-behavior", args.expected_behavior),
        )
        if not value
    ]
    if missing:
        parser.error(f"required for single ID mode: {', '.join(missing)}")

    print(
        build_signal_group_id(
            responsible_agent=args.responsible_agent,
            responsible_owned_skill=args.responsible_owned_skill,
            category=args.category,
            observed_behavior=args.observed_behavior,
            expected_behavior=args.expected_behavior,
        )
    )


if __name__ == "__main__":
    main()

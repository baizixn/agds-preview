---
name: manage-project-memory
description: Maintain a game project's local AI Studio state, context map, tasks, approvals, decisions, handoffs, and agent records without mixing drafts into approved facts. Use when initializing project memory, recording work, handing off between agents, approving results, archiving superseded material, or repairing inconsistent local records.
---

# Manage Project Memory

Use this capability when project records need updating, a real handoff or cross-session recovery is needed, or the project explicitly requires structured recording. Ordinary bounded work may keep its outputs, checks, and limitations in the current task; it does not require a separate memory Agent or event stream. Follow the existing project format and explicit recording requirements without creating a parallel ledger.

1. Read repository rules and current state before changing records.
2. Keep `PROJECT_STATE.md`, `ACTIVE_TASKS.yaml`, and `PENDING_APPROVALS.yaml` current and compact.
3. Write substantial work under `Agent_Records/Working` or `Candidate`.
4. Promote only after explicit owner approval; never treat `Completed` as `Approved`.
5. Record approved directional choices as immutable decision files. Supersede; do not overwrite history.
6. For a real handoff or recovery, retain the objective, verified inputs, output, checks and evidence, remaining risk, next owner, and next action. Use paths instead of copying domain documents.
7. Update `CONTEXT_MAP.md` only when the canonical location or read order changes.
8. Archive stale working records rather than exposing them as current context.
9. Record explicit owner corrections and verified recurring failures in `CAPABILITY_FEEDBACK.yaml`; do not edit the shared plugin directly.

## Append-only task lifecycle events

The following profile applies when the project's existing format or explicit task requires lifecycle events. It does not require every ordinary task or handoff to create an event stream. Maintain one append-only stream per `task_id`; append events when they occur, with `handoff` for a real transfer/recovery and `close` when execution ends. Do not fabricate all three events on a first recording pass. Preserve an explicit project's stricter event requirements and existing chains; these rules do not authorize migration or deletion.

Each event has these required top-level fields:

- stable non-empty `event_id` and `task_id`;
- `event_kind`: `start`, `handoff`, `close`, or `owner_decision`;
- `predecessor`: `null` only for `start`, otherwise the immediately preceding event's `event_id`;
- `recorded_at` and `actor`;
- `context_refs` and `evidence_refs` arrays. Each path-bearing reference is an object with a declared stable `base` such as `target_repo`, `task_output`, or `contract_root`, plus a relative `path`. Never infer a base from the current directory.

Kind-specific payloads stay incremental:

- `start` records the approved objective, working mode, constraints, and acceptance evidence references.
- `handoff` records `delta_outputs`, `delta_evidence`, `unresolved_risks`, `next_owner`, and `next_action`. Its predecessor link and deltas are the canonical continuation point.
- `close` records non-empty `stop_reason`, non-empty `remaining_risks`, `execution_state` exactly equal to `execution_line_closed`, and non-empty `next_owner`. Keep these four fields together in the close node's declared kind-specific payload or, when the record schema uses top-level kind fields, directly on the close node. Do not satisfy the close contract by pointing to an earlier handoff. The close never sets or implies `Approved`.
- `owner_decision` is optional and separate. Append it only after explicit Project Owner input, with the decision, decided scope, owner actor, and decision evidence reference. Never infer it from `close`, `Completed`, a Reviewer recommendation, or silence.

For an ordinary append, read and validate only the changed operational record and this task's chain. Reference project facts by path; do not copy `Game_Documents`, large context blocks, or project-specific facts into shared rules or lifecycle events. A repeated append with the same `event_id` and identical content is an idempotent no-op. The same ID with different content, a duplicate ID, dangling or non-linear predecessor, missing path `base`, or invalid kind fails closed.

Route a formal Project Memory Agent only when repair requires professional record reconstruction: duplicate or conflicting IDs, a broken chain, a missing path base, fidelity-preserving reconstruction of conflicting historical state, legacy-system migration, or bulk index or archive repair. Preserve the original records before producing a repair Candidate. Preserve Candidate versus Approved status, explicit Owner authority, limitations, and unknowns; supersede explicitly and never silently overwrite. The first produced complex-repair Candidate must include a linked `start -> handoff -> close` chain, and its close node must itself carry all four required close fields with non-empty values. Treat any missing or empty close field as a failed repair Candidate even when a structural validator reports success.

Maintain the approved context index and return only paths needed by the authorized task. Direct Skill use does not require an Orchestrator intermediary; it still cannot expand the task's context or authority independently.

Project Memory may update operational records under `AI_Records/`. It must not author or change approved domain conclusions under `Game_Documents/`, approve on behalf of the owner, or promote Candidate output without explicit owner approval.

Before handoff, validate every changed YAML or JSON operational record with `scripts/validate_operational_records.py`. Pass only the explicit changed paths, name every stable record-ID field with `--unique-field`, and name each routed enumeration with `--enum-field FIELD=VALUE1,VALUE2`. The standard-library helper must reject duplicate mapping keys, duplicate configured IDs, invalid configured enumeration values, malformed JSON, and YAML outside its supported parseable subset. Fail closed on an unsupported construct; do not rewrite the record, scan unrelated files, or treat structural validation as authority to reinterpret a domain conclusion. Do not store full game documents in Studio records; link to their project paths. Use `bootstrap-game-project` for project initialization and `evolve-studio-capabilities` for reusable Agent or Skill improvement.

When a changed operational record intentionally stores retained limitations or unknowns alongside current or retained targets, use one explicit collection whose items include `record_id`, `record_kind` (`limitation` or `unknown`), `subject_kind` (`artifact`, `candidate`, or `decision`), non-empty stable `subject_ref`, and non-empty `evidence_scope_refs`. Validate that collection with `--subject-binding-list FIELD`. Never inherit a subject from a neighbor, title, `current`/`latest` alias, file position, or similar prose; never move an older limitation to the current target. A missing or ambiguous binding is structurally invalid for current routing, not permission for Project Memory or the helper to reinterpret the domain result, inspect the referenced evidence, or change its status. Enable this profile only for the explicitly routed collection; do not identify limitations by scanning free text.

Project-memory completion does not imply a version-control commit. Record a real Git or SVN revision only when that system is present and the revision actually exists. For unmanaged directories, record file outputs and validation evidence without a commit field.

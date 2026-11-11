# Project/module framework and memory plan

Use before implementing a project-level or module-level requirement, including a replacement of an existing module. Keep one record with the existing technical decision; do not generate a new report on every turn. A small repair within an unchanged checked design reuses that record. This extends the API-level [capability check](engine-capability-check.md); use that separate record as well when individual engine support or a required executable probe remains uncertain. Neither record replaces technical review where the main Skill requires it.

## Framework decision

1. Inspect the current project architecture, actual engine/package versions, runtime backend and target platform. Preserve established extension points unless evidence supports changing them.
2. Check relevant current first-party documentation and, when the requirement calls for it, maintained ecosystem frameworks at project/module scale. An API result alone is insufficient for a module choice. A fitting inspected existing framework may be the only candidate; do not manufacture a fixed number of alternatives or install a package just to complete a form.
3. Record each considered candidate's version, fit, limitations, maintenance and license, with actual source files or saved primary documentation. For third-party selections, include primary evidence for maintenance and license. Popularity, a model's recollection and a search snippet are insufficient. Source identity checks do not authenticate the publisher or prove suitability; Engineering and independent review still assess those claims.
4. Choose `reuse`, `configure`, `extend`, `adapter`, `fork` or `custom`. Prefer a fitting solution and the smallest supported extension. A custom replacement needs a concrete gap and evidence-backed rejection of a relevant noncustom alternative. Unknown compatibility, version or license cannot justify a new implementation choice. A new dependency or fork needs existing explicit task authority; the checker does not grant it or install anything. Do not silently edit vendor core code.

## Engine-aware memory plan

Keep these points concrete for the affected paths, using inspected files/symbols or a proposed owner for a greenfield design:

- **Engine profile:** version, backend, platform and relevant GC/resource-allocation behavior from applicable primary sources. Managed GC, native allocations and engine resources have different lifetimes; managed reachability alone does not demonstrate resource release.
- **Ownership and lifetimes:** who creates, holds, resets and releases objects, buffers, handles, assets and asynchronous results; include cancelled/failed start, late completion and repeated exit/re-entry.
- **Hot paths and peaks:** high-frequency temporary allocations, collection resizing and overlapping old/new scenes or resources. Plan reuse/capacity, bounded batches, staggered loading or other supported mechanisms only when they fit the workload. State any unavoidable allocation and its expected frequency.
- **Retention limits:** capacity/overflow policy for pools and caches, reset rules, trimming/release point and retained-memory cost. A pool can reduce allocation while increasing memory residency; it is not automatically beneficial.
- **Measurement:** comparable baseline and changed build on the same target, scene, load and settings. Capture frame-time spikes, allocation rate/bytes per frame, GC duration/frequency, peak managed/native/resource memory and retained memory after repeated lifecycle operations as relevant. Choose actual budgets with the project; do not invent universal thresholds or report only averages.

Do not default to manual collections, disabling GC, native/manual allocation or migrating to a different execution model. Such changes need version/platform support, a demonstrated bottleneck and a release/lifecycle plan. For example, [Unity 6.0's GC documentation](https://docs.unity.com/en-us/engine/6000.0/manual/analysis/performance-memory/managed-memory/incremental-garbage-collection) explains that incremental collection spreads work across frames, rather than making collection faster, and has platform limitations. This is an illustration, not a substitute for reading the actual project's version and platform documentation.

## Executable record and commands

The current automatic inventory adapter is Unity. Other engines require a separately supported inventory adapter or an explicitly reviewed manual equivalent; do not fabricate Unity inputs. Paths below are relative to the record's directory; inventory `root` identifies the actual project. Keep real project records outside the shared plugin repository.

```text
python <plugin>/skills/engineer-game/scripts/engine_capability_check.py inspect --root <project> --output <task>/inventory.json
python <plugin>/skills/engineer-game/scripts/engine_capability_check.py check --record <task>/engineering-plan.json --output <task>/plan-check.json
python <plugin>/skills/engineer-game/scripts/engine_capability_check.py guard --record <task>/engineering-plan.json -- <approved-command> <arguments>
```

Use `kind: engineering_plan`, `schema_version: 1`, `inventory`, and:

```json
{
  "kind": "engineering_plan",
  "schema_version": 1,
  "inventory": "inventory.json",
  "task": {
    "id": "module-task-id",
    "source": {"path": "task.md", "sha256": "actual-file-sha256"},
    "level": "module",
    "permission": "implementation"
  },
  "evidence": [
    {"id": "current-code", "kind": "local", "path": "architecture.md", "sha256": "actual-file-sha256"},
    {"id": "framework-doc", "kind": "primary", "path": "framework-doc.txt", "sha256": "actual-file-sha256", "url": "https://publisher.example/versioned-documentation", "issuer": "actual publisher", "version": "actual framework version"}
  ],
  "framework": {
    "existing_evidence": ["current-code"],
    "candidates": [
      {"id": "existing-framework", "origin": "existing", "version": "actual version or source revision", "fit": "fits", "reason": "Actual requirement-to-extension-point assessment", "evidence": ["current-code", "framework-doc"], "maintenance": "current", "license": "compatible"}
    ],
    "selection": {"id": "existing-framework", "strategy": "extend", "reason": "Actual bounded extension", "gaps": [], "dependency_change": false, "change_authority_evidence": []}
  },
  "memory": {
    "engine_profile": "Actual engine/backend/platform allocation and GC behavior",
    "ownership": "Actual owners and release responsibilities",
    "hot_paths": ["Actual path and expected allocation behavior"],
    "allocation_lifetimes": ["Actual allocation and lifetime"],
    "peak_strategy": ["Concrete overlapping-lifetime/peak strategy"],
    "retention_limits": ["Concrete capacity and overflow policy, or reason none applies"],
    "release_paths": ["Actual success/cancellation/re-entry release paths"],
    "measurement_plan": "Actual target, comparable workload and relevant measurements",
    "budget_status": "unknown",
    "budgets": {},
    "validation": {"state": "not_run", "evidence": [], "artifact_id": "", "environment": "", "scenario": "", "metrics": {}}
  }
}
```

Replace illustrative prose and hashes with inspected facts; this example is not valid evidence. Candidate `origin` is `existing|engine|first_party|third_party|custom`; `fit` is `fits|partial|unsuitable|unknown`; maintenance is `current|stale|unknown`; license is `compatible|incompatible|unknown`. `task.level` is `project|module`, permission is `inspect|probe|implementation`.

For a measurement attachment, use evidence `kind: measurement`, actual file path/hash, and `context: {environment_fingerprint: <inventory fingerprint>, task_sha256: <task source hash>}`. A declared memory validation `pass` additionally requires defined nonempty budgets, measurement evidence bound to the current context, build/artifact identity, environment, scenario and metrics. Changed project inventory, task or evidence invalidates the record and requires reassessment. Even a complete receipt checks traceability and declared fields: independent evaluation must still compare the raw measurements with the budgets; it does not automatically prove smoother gameplay or absence of leaks.

An otherwise complete plan with `not_run` measurements can permit authorized implementation and reports performance unverified. A failed or inconclusive measurement may support authorized corrective implementation, never an accepted performance claim. Missing plan/evidence or a fabricated `pass` blocks readiness. The command `guard` only gates commands routed through it; direct Codex edits still need the current result in the task and review packet. It is not an OS-level write interceptor. No check grants Owner acceptance, dependency authority or a new platform strategy.

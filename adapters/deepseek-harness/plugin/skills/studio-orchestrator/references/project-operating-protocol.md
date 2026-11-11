# Project operating protocol

Use this protocol as the reusable baseline for every game project coordinated through AI Game Development Studio. Project-specific rules may narrow it but may not silently weaken owner control or information isolation.

The V1.1 governance background and the current iteration clauses are recorded in [`collaboration-protocol-v1.1-addendum.md`](collaboration-protocol-v1.1-addendum.md). Interpret this protocol together with that addendum and the target project's explicit agreement. Version-specific adoption and deployment require their own evidence.

## Architecture

- The Project Owner controls direction, scope, quality, promotion, and external actions.
- The Studio Orchestrator is the default user-facing coordinator.
- Specialist Agents are temporary bounded workers selected by Skill.
- Local project files are shared memory; no website, online database, or permanent Agent service is required.
- `Game_Documents/` stores approved game facts. `AI_Records/` stores operational state, tasks, approvals, feedback, handoffs, and Agent records.
- Reusable Agent and Skill behavior remains in the plugin, never in a target game's facts.

## Work lifecycle

1. Read repository rules, compact project state, context map, and minimal task-specific documents.
2. Keep one bounded task with objective, owner, inputs, output, relevant checks, and existing authority. Name an approval gate only when a real decision remains; do not create a new task or gate for each repair.
3. Invoke the smallest useful set of Skills and Agents.
4. Keep incomplete output in Working; move self-checked output to Candidate.
5. Verify changed behavior and relevant regressions before handoff. Use independent critique for material results at a coherent checkpoint; routine repairs do not require a separate QA/Reviewer chain.
6. Continue authorized fixes. After two cause-based corrections of the same blocker still fail, or no new useful evidence emerges, pause the current failed approach. Recheck assumptions, actual results, both failures and necessary source/reliable references; adjust the method, using bounded independent advice only when useful. New evidence may support finite in-scope progress. File/commit counts, a renamed task, reworded error or a minor variation of the failed method do not reset this limit. Preserve failures and continue unrelated authorized work.
7. After that reassessment, ask the Owner only if no viable method remains or a concrete decision changes scope, architecture tradeoffs, cost, authority or quality. Do not transfer ordinary investigation to the Owner. Requests for external actions must also stay within existing authority.
8. Complete ordinary tasks and continue authorized testing without a per-fix Owner decision. Formal adoption still requires explicit Owner authority, which may already cover the exact action. Successful checks are evidence, not an invented approval.

For early development, apply the three work classes in [Owner interaction](../SKILL.md#owner-interaction). This is the interpretation of the addendum's approval gates for iteration; it does not migrate or weaken a target project's explicit operating agreement.

## Information integrity

- Approved domain documents are facts. Chat, Working, Candidate, and superseded records are not.
- Load only relevant context. Do not read all history by default.
- Mark assumptions and unknowns; never fill gaps with plausible invention.
- Cross-discipline changes return as Candidate findings instead of silent edits to another discipline's approved facts.
- Delete valueless transition copies and placeholder archives. Archive only material with real traceability value.

## Capability evolution

- Separate task-output revision from reusable Agent or Skill improvement.
- Capture explicit owner corrections, repeated failures, avoidable context cost, missing capability, and validation gaps as evidence.
- Generalize only when evidence supports cross-project value.
- Test improvements in isolation and keep project-specific facts out of the plugin.
- Require owner approval before adopting a capability Candidate into the shared plugin baseline.

## Version control

- Detect Git, SVN, or an unmanaged directory before version-control operations.
- A real worktree may provide status and history evidence, but commits and remote mutations still require user authorization.
- An unmanaged directory needs no commit and must not be initialized into version control unless the owner asks.
- Task completion, owner approval, and repository commit are separate states.

## Required project agreement

Each initialized project should maintain `AI_Records/OPERATING_AGREEMENT.md` as its adopted local agreement and route Studio-governance questions to it through `AI_Records/CONTEXT_MAP.md`.

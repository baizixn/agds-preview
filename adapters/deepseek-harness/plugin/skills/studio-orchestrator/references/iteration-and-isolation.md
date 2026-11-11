# Iteration and isolation

## Information tiers

1. **Approved**: owner-approved project facts and validated implementation evidence.
2. **Candidate**: proposal not yet formally adopted; authorized testing and revision may continue without waiting for adoption.
3. **Working**: private draft, experiment, scratch analysis, or incomplete output.
4. **Archived**: superseded history, readable only when needed.

Never infer approval from file existence, agent confidence, or task completion.

## Controlled iteration

- Pass 1: produce against the task acceptance criteria.
- Pass 2: self-check for contradictions, missing evidence, scope drift, and project constraints.
- Review: for material work, use a fresh reviewer with only the task, approved context, candidate artifact, evidence, and acceptance criteria at a coherent checkpoint. Routine reversible repairs use proportionate self-checks, unless the explicit task requires independent review.
- Revision: fix in-scope findings and rerun affected checks without asking the Owner to authorize each repair.
- After two cause-based corrections of the same blocker still fail, or yield no new useful evidence, pause the current failed approach. Recheck assumptions, actual results, both failures and necessary source/reliable references, then adjust the method. Bounded independent advice is optional. Continue a finite in-scope step only with new supporting evidence. File/commit counts, renamed tasks, reworded errors or small variations of the same failed method do not reset the limit. Preserve failures; unrelated authorized work may continue. Ask the Owner for a specific decision only if no viable method remains or scope, architecture tradeoffs, cost, authority or quality must change.

## Minimal task packet

Include task ID, objective, acceptance criteria, allowed inputs, constraints, output path, and prohibited decisions. Exclude unrelated chat, other agents' speculative notes, and the desired verdict.

## Promotion

Only the orchestrator promotes a Candidate under explicit Owner authority covering that action and scope. Reuse existing authorization when applicable. Promotion updates the formal artifact, decision record when needed, task state, project state, and handoff. Ordinary completion and the next authorized iteration do not require promotion; do not manufacture a pending approval to close a routine task. See [Owner interaction](../SKILL.md#owner-interaction).

# {{PROJECT_NAME}} AI Game Development Studio operating agreement

- Effective date: {{DATE}}
- Approval owner: Project Owner

## Boundaries

- `Game_Documents/` stores approved game facts and formal domain documents.
- `AI_Records/` stores local AI state, tasks, approvals, feedback, handoffs, and Agent records.
- Reusable Agent and Skill behavior stays in the AI Game Development Studio plugin.
- Local files are the shared project memory; no online database is required.

## Workflow

1. The Project Owner gives the goal and retains final direction and quality control.
2. The task uses minimal context and the relevant professional Skills directly; use Studio Orchestrator when cross-discipline coordination is needed or explicitly requested.
3. Specialist output moves from Working to Candidate after self-check and proportionate review.
4. Material uncertainty returns to the Project Owner. A Candidate becomes a project fact only after explicit approval.
5. Engineering results distinguish implemented, locally verified, and device/player verified states.

## Isolation and iteration

- Approved documents are facts; Working, Candidate, chat, and superseded records are not.
- Do not read all history or unrelated Agent records by default.
- Continue authorized repairs and checks. Two rounds means cause-based corrections of the same blocker, not files, commits or total edits. After two unsuccessful rounds or no new useful evidence, pause the current failed approach; inspect assumptions, results, both failures and necessary source/reliable references, then change method. Bounded independent advice is optional. New evidence may justify finite in-scope progress; renaming the task/error or slightly varying the failed approach does not reset the limit. Ask the Owner for a specific decision only if no viable method remains or scope, architecture tradeoffs, cost, authority or quality must change. Preserve failures and continue unrelated authorized work.
- Reusable Agent or Skill evolution requires evidence, isolated validation, and Project Owner approval before adoption.

## Version control

- Detect Git, SVN, or an unmanaged directory before repository actions.
- Commits and remote changes require Project Owner authorization.
- An unmanaged directory requires no commit and must not be initialized into version control unless requested.
- Task completion, approval, and commit are separate states.

## Maintenance

Record current state in `PROJECT_STATE.md`, tasks in `ACTIVE_TASKS.yaml`, approvals in `PENDING_APPROVALS.yaml`, and reusable capability evidence in `CAPABILITY_FEEDBACK.yaml`. Update this agreement through an explicit decision when its policy changes.
